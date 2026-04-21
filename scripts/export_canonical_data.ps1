[CmdletBinding()]
param(
    [string]$ProjectRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ProjectRoot = Split-Path -Parent $scriptDirectory
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Get-Sha256Hex {
    param([string]$Text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
    }
    finally {
        $sha.Dispose()
    }
}

function Normalize-KeyText {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ''
    }
    return ($Value.Trim().ToLowerInvariant() -replace '\s+', ' ')
}

function Normalize-Email {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ''
    }
    return $Value.Trim().ToLowerInvariant()
}

function Get-EmailDomain {
    param([string]$Email)
    if ($Email -match '@([^@\s]+)$') {
        return $matches[1].ToLowerInvariant()
    }
    return ''
}

function Normalize-Phone {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ''
    }

    $digits = ($Value -replace '\D', '')
    if ([string]::IsNullOrWhiteSpace($digits)) {
        return ''
    }

    if ($digits.Length -eq 10 -or $digits.Length -eq 11) {
        return "+55$digits"
    }
    if (($digits.Length -eq 12 -or $digits.Length -eq 13) -and $digits.StartsWith('55')) {
        return "+$digits"
    }
    if ($digits.Length -gt 13) {
        return ''
    }
    return ''
}

function Convert-ExcelDateValue {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ''
    }
    $trimmed = $Value.Trim()
    $number = 0.0
    if ([double]::TryParse($trimmed, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$number)) {
        $base = [datetime]'1899-12-30'
        return $base.AddDays($number).ToString('yyyy-MM-ddTHH:mm:ss')
    }
    $parsed = [datetime]::MinValue
    if ([datetime]::TryParse($trimmed, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::AssumeLocal, [ref]$parsed)) {
        return $parsed.ToString('yyyy-MM-ddTHH:mm:ss')
    }
    return $trimmed
}

function Get-BirthYear {
    param([string]$DateValue)
    if ([string]::IsNullOrWhiteSpace($DateValue)) {
        return ''
    }
    $parsed = [datetime]::MinValue
    if ([datetime]::TryParse($DateValue, [ref]$parsed)) {
        return [string]$parsed.Year
    }
    return ''
}

function New-PersonKey {
    param(
        [string]$Name,
        [string]$Email,
        [string]$Phone
    )
    return (Get-Sha256Hex ("person|" + (Normalize-KeyText $Name) + "|" + (Normalize-Email $Email) + "|" + ($Phone -replace '\D', '')))
}

function New-PartnerKey {
    param(
        [string]$Name,
        [string]$Email,
        [string]$Instagram
    )
    return (Get-Sha256Hex ("partner|" + (Normalize-KeyText $Name) + "|" + (Normalize-Email $Email) + "|" + (Normalize-KeyText $Instagram)))
}

function Split-CityState {
    param([string]$Raw)

    $result = [ordered]@{
        cidade = ''
        estado = ''
        endereco_raw = $Raw
    }

    if ([string]::IsNullOrWhiteSpace($Raw)) {
        return [pscustomobject]$result
    }

    if ($Raw -match '\|') {
        $parts = @($Raw -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
        if ($parts.Count -ge 2) {
            $result.cidade = $parts[-2]
            $result.estado = $parts[-1]
        }
        return [pscustomobject]$result
    }

    if ($Raw -match ',\s*([A-Z]{2})$') {
        $result.estado = $matches[1]
        $beforeState = $Raw.Substring(0, $Raw.Length - 2).TrimEnd(',').Trim()
        $segments = @($beforeState -split ',')
        if ($segments.Count -gt 0) {
            $result.cidade = $segments[-1].Trim()
        }
        return [pscustomobject]$result
    }

    return [pscustomobject]$result
}

function Convert-ExcelColumnToNumber {
    param([string]$Column)
    $n = 0
    foreach ($ch in $Column.ToCharArray()) {
        $n = ($n * 26) + ([int][char]::ToUpperInvariant($ch) - [int][char]'A' + 1)
    }
    return $n
}

function Convert-ExcelRefToCoords {
    param([string]$Ref)
    if ($Ref -match '^([A-Z]+)(\d+)$') {
        return [pscustomobject]@{
            Col = Convert-ExcelColumnToNumber $matches[1]
            Row = [int]$matches[2]
        }
    }
    throw "Referencia de celula invalida: $Ref"
}

function Parse-Range {
    param([string]$RangeRef)
    $parts = $RangeRef -split ':'
    return [pscustomobject]@{
        Start = Convert-ExcelRefToCoords $parts[0]
        End   = Convert-ExcelRefToCoords $parts[1]
    }
}

function Open-XlsxWorkbook {
    param([string]$LiteralPath)

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $resolved = (Resolve-Path -LiteralPath $LiteralPath).Path
    $zip = [System.IO.Compression.ZipFile]::OpenRead($resolved)
    $entries = @{}
    foreach ($entry in $zip.Entries) {
        $entries[$entry.FullName] = $entry
    }

    $sharedStrings = @()
    if ($entries.ContainsKey('xl/sharedStrings.xml')) {
        [xml]$ssXml = New-Object xml
        $ssReader = New-Object System.IO.StreamReader($entries['xl/sharedStrings.xml'].Open())
        $ssXml.LoadXml($ssReader.ReadToEnd())
        $ssReader.Close()
        foreach ($si in $ssXml.sst.si) {
            $sharedStrings += [string]$si.InnerText
        }
    }

    [xml]$wbXml = New-Object xml
    $wbReader = New-Object System.IO.StreamReader($entries['xl/workbook.xml'].Open())
    $wbXml.LoadXml($wbReader.ReadToEnd())
    $wbReader.Close()

    [xml]$relsXml = New-Object xml
    $relsReader = New-Object System.IO.StreamReader($entries['xl/_rels/workbook.xml.rels'].Open())
    $relsXml.LoadXml($relsReader.ReadToEnd())
    $relsReader.Close()

    $relMap = @{}
    foreach ($rel in $relsXml.Relationships.Relationship) {
        $target = [string]$rel.Target
        if ($target -notlike 'xl/*') {
            $target = 'xl/' + $target.TrimStart('/').Replace('../', '')
        }
        $relMap[[string]$rel.Id] = $target
    }

    $ns = New-Object System.Xml.XmlNamespaceManager($wbXml.NameTable)
    $ns.AddNamespace('d', 'http://schemas.openxmlformats.org/spreadsheetml/2006/main')
    $ns.AddNamespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')

    $sheets = @{}
    foreach ($sheet in $wbXml.SelectNodes('//d:sheets/d:sheet', $ns)) {
        $relId = $sheet.GetAttribute('id', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        $sheets[[string]$sheet.name] = $relMap[$relId]
    }

    return [pscustomobject]@{
        Path          = $resolved
        Zip           = $zip
        Entries       = $entries
        SharedStrings = $sharedStrings
        Sheets        = $sheets
    }
}

function Close-XlsxWorkbook {
    param($Workbook)
    if ($null -ne $Workbook.Zip) {
        $Workbook.Zip.Dispose()
    }
}

function Get-CellValue {
    param(
        $Cell,
        [string[]]$SharedStrings
    )
    $type = ''
    if ($Cell.PSObject.Properties.Name -contains 't') {
        $type = [string]$Cell.t
    }
    if ($type -eq 's') {
        if ($Cell.PSObject.Properties.Name -contains 'v') {
            return $SharedStrings[[int]$Cell.v]
        }
        return ''
    }
    if ($type -eq 'inlineStr') {
        if ($Cell.PSObject.Properties.Name -contains 'is') {
            return [string]$Cell.is.InnerText
        }
        return ''
    }
    if (($Cell.PSObject.Properties.Name -contains 'v') -and $Cell.v) {
        return [string]$Cell.v
    }
    return [string]$Cell.InnerText
}

function Get-SheetRows {
    param(
        $Workbook,
        [string]$SheetName
    )

    [xml]$sheetXml = New-Object xml
    $sheetReader = New-Object System.IO.StreamReader($Workbook.Entries[$Workbook.Sheets[$SheetName]].Open())
    $sheetXml.LoadXml($sheetReader.ReadToEnd())
    $sheetReader.Close()

    $rows = @{}
    foreach ($row in $sheetXml.worksheet.sheetData.row) {
        $cells = @{}
        foreach ($cell in $row.c) {
            $coords = Convert-ExcelRefToCoords ([string]$cell.r)
            $cells[$coords.Col] = Get-CellValue -Cell $cell -SharedStrings $Workbook.SharedStrings
        }
        $rows[[int]$row.r] = $cells
    }
    return $rows
}

function Get-RangeObjects {
    param(
        [hashtable]$Rows,
        [string]$RangeRef,
        [string[]]$Headers,
        [bool]$HasHeaderRow
    )

    $range = Parse-Range $RangeRef

    $headerNames = @()
    if ($HasHeaderRow) {
        for ($col = $range.Start.Col; $col -le $range.End.Col; $col++) {
            $value = ''
            if ($Rows.ContainsKey($range.Start.Row) -and $Rows[$range.Start.Row].ContainsKey($col)) {
                $value = [string]$Rows[$range.Start.Row][$col]
            }
            if ([string]::IsNullOrWhiteSpace($value)) {
                $value = "column_$col"
            }
            $headerNames += $value
        }
        $startRow = $range.Start.Row + 1
    }
    else {
        $headerNames = $Headers
        $startRow = $range.Start.Row
    }

    $objects = @()
    for ($rowIndex = $startRow; $rowIndex -le $range.End.Row; $rowIndex++) {
        $record = [ordered]@{}
        $nonEmpty = 0
        for ($offset = 0; $offset -lt $headerNames.Count; $offset++) {
            $colIndex = $range.Start.Col + $offset
            $value = ''
            if ($Rows.ContainsKey($rowIndex) -and $Rows[$rowIndex].ContainsKey($colIndex)) {
                $value = [string]$Rows[$rowIndex][$colIndex]
            }
            if (-not [string]::IsNullOrWhiteSpace($value)) {
                $nonEmpty++
            }
            $record[$headerNames[$offset]] = $value
        }
        if ($nonEmpty -gt 0) {
            $objects += [pscustomobject]$record
        }
    }
    return $objects
}

function Export-RestrictedCsv {
    param(
        [string]$OutputPath,
        [object[]]$Records
    )
    if ($Records.Count -eq 0) {
        @() | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8
        return
    }
    $Records | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8
}

$contextRoot = Join-Path $ProjectRoot 'Tour4friends-context'

function Resolve-FirstFile {
    param(
        [string]$Directory,
        [string]$Filter
    )
    $match = Get-ChildItem -LiteralPath $Directory -File -Filter $Filter | Select-Object -First 1
    if ($null -eq $match) {
        throw "Arquivo nao encontrado com filtro '$Filter' em '$Directory'"
    }
    return $match.FullName
}

function Get-WorkbookSheetName {
    param(
        $Workbook,
        [string]$Pattern
    )
    $match = @($Workbook.Sheets.Keys | Where-Object { $_ -like $Pattern }) | Select-Object -First 1
    if ([string]::IsNullOrWhiteSpace($match)) {
        throw "Aba nao encontrada com padrao '$Pattern' no workbook '$($Workbook.Path)'"
    }
    return $match
}

function Get-RowValue {
    param(
        $Row,
        [string[]]$Patterns
    )
    foreach ($pattern in $Patterns) {
        $property = $Row.PSObject.Properties | Where-Object { $_.Name -like $pattern } | Select-Object -First 1
        if ($null -ne $property) {
            return [string]$property.Value
        }
    }
    return ''
}

$restrictedOutput = Join-Path $ProjectRoot 'data\canonical\csv\restricted'
Ensure-Directory $restrictedOutput

$mailWorkbookPath = Resolve-FirstFile -Directory $contextRoot -Filter '*T4F_mail_marketing.xlsx'
$prospectWorkbookPath = Resolve-FirstFile -Directory $contextRoot -Filter 'Planilhas_Prospeccao_Segmento_Tour4friends.xlsx'

$mailWorkbook = Open-XlsxWorkbook -LiteralPath $mailWorkbookPath
$prospectWorkbook = Open-XlsxWorkbook -LiteralPath $prospectWorkbookPath

try {
    $sheet100Agencias = Get-WorkbookSheetName -Workbook $mailWorkbook -Pattern '100 agencias'
    $sheetClientes = Get-WorkbookSheetName -Workbook $mailWorkbook -Pattern 'Clientes Antigos'
    $sheetContatos2026 = Get-WorkbookSheetName -Workbook $mailWorkbook -Pattern 'Contatos 2026'
    $sheetContatos2026I = Get-WorkbookSheetName -Workbook $mailWorkbook -Pattern 'Contatos 2026 I'
    $sheetBikeOutros = Get-WorkbookSheetName -Workbook $mailWorkbook -Pattern 'Bike outros estados'
    $sheetGrupos = Get-WorkbookSheetName -Workbook $mailWorkbook -Pattern '100 Grupos Catolicos*'
    $sheetBikeClass = Get-WorkbookSheetName -Workbook $mailWorkbook -Pattern '100 bike class'

    $sheetFranciscanos = Get-WorkbookSheetName -Workbook $prospectWorkbook -Pattern 'Franciscanos'
    $sheetAssociacoes = Get-WorkbookSheetName -Workbook $prospectWorkbook -Pattern 'Caminhos*'
    $sheetNovosParceiros = Get-WorkbookSheetName -Workbook $prospectWorkbook -Pattern 'Novos_100_Parceiros_SP'
    $sheetDevotos = Get-WorkbookSheetName -Workbook $prospectWorkbook -Pattern 'Devotos_Carlo_Acutis'
    $sheetConsolidado = Get-WorkbookSheetName -Workbook $prospectWorkbook -Pattern 'Contatos_Existentes_SP_11'

    $mailRows100Agencias = Get-SheetRows -Workbook $mailWorkbook -SheetName $sheet100Agencias
    $mailRowsClientes = Get-SheetRows -Workbook $mailWorkbook -SheetName $sheetClientes
    $mailRowsContatos2026 = Get-SheetRows -Workbook $mailWorkbook -SheetName $sheetContatos2026
    $mailRowsContatos2026I = Get-SheetRows -Workbook $mailWorkbook -SheetName $sheetContatos2026I
    $mailRowsBikeOutros = Get-SheetRows -Workbook $mailWorkbook -SheetName $sheetBikeOutros
    $mailRowsGrupos = Get-SheetRows -Workbook $mailWorkbook -SheetName $sheetGrupos
    $mailRowsBikeClass = Get-SheetRows -Workbook $mailWorkbook -SheetName $sheetBikeClass

    $prospectRowsFranciscanos = Get-SheetRows -Workbook $prospectWorkbook -SheetName $sheetFranciscanos
    $prospectRowsAssociacoes = Get-SheetRows -Workbook $prospectWorkbook -SheetName $sheetAssociacoes
    $prospectRowsNovosParceiros = Get-SheetRows -Workbook $prospectWorkbook -SheetName $sheetNovosParceiros
    $prospectRowsDevotos = Get-SheetRows -Workbook $prospectWorkbook -SheetName $sheetDevotos
    $prospectRowsConsolidado = Get-SheetRows -Workbook $prospectWorkbook -SheetName $sheetConsolidado

    $agencias = Get-RangeObjects -Rows $mailRows100Agencias -RangeRef 'A1:G101' -Headers @() -HasHeaderRow $true
    $clientesAntigos = Get-RangeObjects -Rows $mailRowsClientes -RangeRef 'A1:AJ94' -Headers @() -HasHeaderRow $true
    $contatos2026 = Get-RangeObjects -Rows $mailRowsContatos2026 -RangeRef 'A1:X107' -Headers @() -HasHeaderRow $true
    $contatos2026IBlock1 = Get-RangeObjects -Rows $mailRowsContatos2026I -RangeRef 'A1:J89' -Headers @() -HasHeaderRow $true
    $contatos2026IBlock2 = Get-RangeObjects -Rows $mailRowsContatos2026I -RangeRef 'A101:G109' -Headers @('lead_legacy_id', 'nome_completo', 'email', 'whatsapp_raw', 'mensagem_interesse', 'consentimento_status', 'submitted_at_raw') -HasHeaderRow $false
    $contatos2026IBlock3 = Get-RangeObjects -Rows $mailRowsContatos2026I -RangeRef 'A113:H119' -Headers @() -HasHeaderRow $true
    $bikeOutros = Get-RangeObjects -Rows $mailRowsBikeOutros -RangeRef 'A1:J101' -Headers @('legacy_id', 'nome_organizacao', 'categoria', 'email_ou_canal', 'instagram', 'telefone_raw', 'modelo_contato', 'localidade_raw', 'perfil_publico', 'observacoes') -HasHeaderRow $false
    $gruposCatolicos = Get-RangeObjects -Rows $mailRowsGrupos -RangeRef 'A1:G101' -Headers @() -HasHeaderRow $true
    $bikeClass = Get-RangeObjects -Rows $mailRowsBikeClass -RangeRef 'A1:G101' -Headers @() -HasHeaderRow $true

    $franciscanos = Get-RangeObjects -Rows $prospectRowsFranciscanos -RangeRef 'A1:G101' -Headers @() -HasHeaderRow $true
    $associacoes = Get-RangeObjects -Rows $prospectRowsAssociacoes -RangeRef 'A1:G101' -Headers @() -HasHeaderRow $true
    $novosParceiros = Get-RangeObjects -Rows $prospectRowsNovosParceiros -RangeRef 'A1:G101' -Headers @() -HasHeaderRow $true
    $devotos = Get-RangeObjects -Rows $prospectRowsDevotos -RangeRef 'A1:G101' -Headers @() -HasHeaderRow $true
    $consolidado = Get-RangeObjects -Rows $prospectRowsConsolidado -RangeRef 'A1:E204' -Headers @() -HasHeaderRow $true

    $sourceRegistry = @(
        [pscustomobject]@{ source_file = 'Cópia de  T4F_mail_marketing.xlsx'; source_sheet = '100 agencias'; entity = 'partner'; source_truth_role = 'primary'; record_classification = 'real_candidate'; notes = 'Agencias e operadoras' }
        [pscustomobject]@{ source_file = 'Cópia de  T4F_mail_marketing.xlsx'; source_sheet = 'Clientes Antigos'; entity = 'customer'; source_truth_role = 'primary'; record_classification = 'real_operational'; notes = 'Historico de clientes' }
        [pscustomobject]@{ source_file = 'Cópia de  T4F_mail_marketing.xlsx'; source_sheet = 'Contatos 2026'; entity = 'customer'; source_truth_role = 'primary'; record_classification = 'real_operational'; notes = 'Intake operacional 2026' }
        [pscustomobject]@{ source_file = 'Cópia de  T4F_mail_marketing.xlsx'; source_sheet = 'Contatos 2026 I'; entity = 'lead'; source_truth_role = 'primary'; record_classification = 'real_operational'; notes = 'Aba com 3 blocos lógicos' }
        [pscustomobject]@{ source_file = 'Cópia de  T4F_mail_marketing.xlsx'; source_sheet = 'Bike outros estados'; entity = 'partner'; source_truth_role = 'primary'; record_classification = 'real_candidate'; notes = 'Schema inferido na camada canonica' }
        [pscustomobject]@{ source_file = 'Cópia de  T4F_mail_marketing.xlsx'; source_sheet = '100 Grupos Catolicos +Classe tr'; entity = 'partner'; source_truth_role = 'primary'; record_classification = 'real_candidate'; notes = 'Prospecção religiosa e premium' }
        [pscustomobject]@{ source_file = 'Cópia de  T4F_mail_marketing.xlsx'; source_sheet = '100 bike class'; entity = 'partner'; source_truth_role = 'primary'; record_classification = 'real_candidate'; notes = 'Prospecção bike' }
        [pscustomobject]@{ source_file = 'Planilhas_Prospeccao_Segmento_Tour4friends.xlsx'; source_sheet = 'Contatos_Existentes_SP_11'; entity = 'partner'; source_truth_role = 'derived_reference'; record_classification = 'derived'; notes = 'Consolidado derivado de fontes primarias' }
        [pscustomobject]@{ source_file = 'Planilhas_Prospeccao_Segmento_Tour4friends.xlsx'; source_sheet = 'Franciscanos'; entity = 'partner'; source_truth_role = 'secondary'; record_classification = 'synthetic_mock_likely'; notes = 'Dominios e padroes indicam base simulada' }
        [pscustomobject]@{ source_file = 'Planilhas_Prospeccao_Segmento_Tour4friends.xlsx'; source_sheet = 'Caminhos e Associações'; entity = 'partner'; source_truth_role = 'secondary'; record_classification = 'synthetic_mock_likely'; notes = 'Dominios e padroes indicam base simulada' }
        [pscustomobject]@{ source_file = 'Planilhas_Prospeccao_Segmento_Tour4friends.xlsx'; source_sheet = 'Novos_100_Parceiros_SP'; entity = 'partner'; source_truth_role = 'secondary'; record_classification = 'synthetic_mock_likely'; notes = 'Dominios e padroes indicam base simulada' }
        [pscustomobject]@{ source_file = 'Planilhas_Prospeccao_Segmento_Tour4friends.xlsx'; source_sheet = 'Devotos_Carlo_Acutis'; entity = 'partner'; source_truth_role = 'secondary'; record_classification = 'synthetic_mock_likely'; notes = 'Dominios e padroes indicam base simulada' }
    )

    $partners = @()

    foreach ($row in $agencias) {
        $address = Get-RowValue -Row $row -Patterns @('Endere*')
        $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('E-mail'))
        $phoneRaw = Get-RowValue -Row $row -Patterns @('Telefone')
        $phone = Normalize-Phone $phoneRaw
        $instagram = Get-RowValue -Row $row -Patterns @('Instagram')
        $name = Get-RowValue -Row $row -Patterns @('Nome da Empresa')
        $perfil = Get-RowValue -Row $row -Patterns @('Perfil')
        $location = Split-CityState $address
        $partners += [pscustomobject]@{
            partner_id            = New-PartnerKey -Name $name -Email $email -Instagram $instagram
            source_file           = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet          = '100 agencias'
            source_dataset        = '100_agencias'
            record_classification = 'real_candidate'
            nome_organizacao      = $name
            categoria             = 'Agencia'
            perfil                = $perfil
            email                 = $email
            email_domain          = Get-EmailDomain $email
            telefone_raw          = $phoneRaw
            whatsapp_e164         = $phone
            instagram             = $instagram
            endereco_raw          = $location.endereco_raw
            cidade                = $location.cidade
            estado                = $location.estado
            contato_modelo        = ''
            observacoes           = ''
        }
    }

    foreach ($row in $gruposCatolicos) {
        $address = Get-RowValue -Row $row -Patterns @('Endere*')
        $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('E-mail'))
        $phoneRaw = Get-RowValue -Row $row -Patterns @('Telefone / WhatsApp')
        $phone = Normalize-Phone $phoneRaw
        $name = Get-RowValue -Row $row -Patterns @('Organi*')
        $categoria = Get-RowValue -Row $row -Patterns @('Categoria')
        $instagram = Get-RowValue -Row $row -Patterns @('Instagram')
        $location = Split-CityState $address
        $partners += [pscustomobject]@{
            partner_id            = New-PartnerKey -Name $name -Email $email -Instagram $instagram
            source_file           = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet          = '100 Grupos Catolicos +Classe tr'
            source_dataset        = '100_grupos_catolicos_classe_tr'
            record_classification = 'real_candidate'
            nome_organizacao      = $name
            categoria             = $categoria
            perfil                = ''
            email                 = $email
            email_domain          = Get-EmailDomain $email
            telefone_raw          = $phoneRaw
            whatsapp_e164         = $phone
            instagram             = $instagram
            endereco_raw          = $location.endereco_raw
            cidade                = $location.cidade
            estado                = $location.estado
            contato_modelo        = ''
            observacoes           = ''
        }
    }

    foreach ($row in $bikeClass) {
        $address = Get-RowValue -Row $row -Patterns @('Endere*')
        $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('E-mail'))
        $phoneRaw = Get-RowValue -Row $row -Patterns @('Telefone / WhatsApp')
        $phone = Normalize-Phone $phoneRaw
        $name = Get-RowValue -Row $row -Patterns @('Organi*')
        $categoria = Get-RowValue -Row $row -Patterns @('Categoria')
        $instagram = Get-RowValue -Row $row -Patterns @('Instagram')
        $location = Split-CityState $address
        $partners += [pscustomobject]@{
            partner_id            = New-PartnerKey -Name $name -Email $email -Instagram $instagram
            source_file           = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet          = '100 bike class'
            source_dataset        = '100_bike_class'
            record_classification = 'real_candidate'
            nome_organizacao      = $name
            categoria             = $categoria
            perfil                = ''
            email                 = $email
            email_domain          = Get-EmailDomain $email
            telefone_raw          = $phoneRaw
            whatsapp_e164         = $phone
            instagram             = $instagram
            endereco_raw          = $location.endereco_raw
            cidade                = $location.cidade
            estado                = $location.estado
            contato_modelo        = ''
            observacoes           = ''
        }
    }

    foreach ($row in $bikeOutros) {
        $location = Split-CityState $row.localidade_raw
        $emailOrChannel = [string]$row.email_ou_canal
        $email = if ($emailOrChannel -match '@') { Normalize-Email $emailOrChannel } else { '' }
        $partners += [pscustomobject]@{
            partner_id            = New-PartnerKey -Name ([string]$row.nome_organizacao) -Email $email -Instagram ([string]$row.instagram)
            source_file           = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet          = 'Bike outros estados'
            source_dataset        = 'bike_outros_estados'
            record_classification = 'real_candidate'
            nome_organizacao      = [string]$row.nome_organizacao
            categoria             = [string]$row.categoria
            perfil                = [string]$row.perfil_publico
            email                 = $email
            email_domain          = Get-EmailDomain $email
            telefone_raw          = [string]$row.telefone_raw
            whatsapp_e164         = Normalize-Phone $row.telefone_raw
            instagram             = [string]$row.instagram
            endereco_raw          = [string]$row.localidade_raw
            cidade                = $location.cidade
            estado                = $location.estado
            contato_modelo        = [string]$row.modelo_contato
            observacoes           = [string]$row.observacoes
        }
    }

    foreach ($dataset in @(
        @{ Name = 'Franciscanos'; SourceDataset = 'franciscanos'; Classification = 'synthetic_mock_likely'; Rows = $franciscanos },
        @{ Name = 'Caminhos e Associações'; SourceDataset = 'caminhos_e_associacoes'; Classification = 'synthetic_mock_likely'; Rows = $associacoes },
        @{ Name = 'Novos_100_Parceiros_SP'; SourceDataset = 'novos_100_parceiros_sp'; Classification = 'synthetic_mock_likely'; Rows = $novosParceiros },
        @{ Name = 'Devotos_Carlo_Acutis'; SourceDataset = 'devotos_carlo_acutis'; Classification = 'synthetic_mock_likely'; Rows = $devotos }
    )) {
        foreach ($row in $dataset.Rows) {
            $address = Get-RowValue -Row $row -Patterns @('Endere*')
            $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('E-mail'))
            $phoneRaw = Get-RowValue -Row $row -Patterns @('Telefone / WhatsApp')
            $phone = Normalize-Phone $phoneRaw
            $name = Get-RowValue -Row $row -Patterns @('Organi*')
            $categoria = Get-RowValue -Row $row -Patterns @('Categoria')
            $instagram = Get-RowValue -Row $row -Patterns @('Instagram')
            $location = Split-CityState $address
            $partners += [pscustomobject]@{
                partner_id            = New-PartnerKey -Name $name -Email $email -Instagram $instagram
                source_file           = 'Planilhas_Prospeccao_Segmento_Tour4friends.xlsx'
                source_sheet          = $dataset.Name
                source_dataset        = $dataset.SourceDataset
                record_classification = $dataset.Classification
                nome_organizacao      = $name
                categoria             = $categoria
                perfil                = ''
                email                 = $email
                email_domain          = Get-EmailDomain $email
                telefone_raw          = $phoneRaw
                whatsapp_e164         = $phone
                instagram             = $instagram
                endereco_raw          = $location.endereco_raw
                cidade                = $location.cidade
                estado                = $location.estado
                contato_modelo        = ''
                observacoes           = ''
            }
        }
    }

    $partners = $partners | Sort-Object partner_id -Unique

    $leads = @()
    foreach ($row in $contatos2026IBlock1) {
        $name = Get-RowValue -Row $row -Patterns @('Nome:')
        $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('Email:'))
        $phoneRaw = Get-RowValue -Row $row -Patterns @('WhatsApp:')
        $phone = Normalize-Phone $phoneRaw
        $intencao = Get-RowValue -Row $row -Patterns @('Como pretende fazer o Caminho:')
        $forma = Get-RowValue -Row $row -Patterns @('Forma de fazer o Caminho:')
        $caminho = Get-RowValue -Row $row -Patterns @('Qual o Caminho do seu interesse:')
        $mensagem = Get-RowValue -Row $row -Patterns @('Como podemos ajud*')
        $consentimento = Get-RowValue -Row $row -Patterns @('Termo de uso')
        $submittedRaw = Get-RowValue -Row $row -Patterns @('DATE')
        $leads += [pscustomobject]@{
            lead_id                              = New-PersonKey -Name $name -Email $email -Phone $phoneRaw
            source_file                          = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet                         = 'Contatos 2026 I'
            source_dataset                       = 'contatos_2026_i_bloco_1'
            source_block                         = 'bloco_1'
            record_classification                = 'real_operational'
            lead_legacy_id                       = Get-RowValue -Row $row -Patterns @('ID')
            nome_completo                        = $name
            email                                = $email
            email_domain                         = Get-EmailDomain $email
            whatsapp_raw                         = $phoneRaw
            whatsapp_e164                        = $phone
            intencao_viagem_raw                  = $intencao
            intencao_viagem_label                = ''
            forma_viagem_raw                     = $forma
            forma_viagem_label                   = ''
            caminho_interesse_raw                = $caminho
            caminho_interesse_label              = ''
            mensagem_interesse                   = $mensagem
            consentimento_status                 = $consentimento
            submitted_at_raw                     = $submittedRaw
            submitted_at_iso                     = Convert-ExcelDateValue $submittedRaw
            mapping_status_intencao_viagem       = 'pending_business_definition'
            mapping_status_forma_viagem          = 'pending_business_definition'
            mapping_status_caminho_interesse     = 'pending_business_definition'
        }
    }

    foreach ($row in $contatos2026IBlock2) {
        $email = Normalize-Email $row.email
        $phone = Normalize-Phone $row.whatsapp_raw
        $leads += [pscustomobject]@{
            lead_id                              = New-PersonKey -Name ([string]$row.nome_completo) -Email $email -Phone ([string]$row.whatsapp_raw)
            source_file                          = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet                         = 'Contatos 2026 I'
            source_dataset                       = 'contatos_2026_i_bloco_2'
            source_block                         = 'bloco_2'
            record_classification                = 'real_operational'
            lead_legacy_id                       = [string]$row.lead_legacy_id
            nome_completo                        = [string]$row.nome_completo
            email                                = $email
            email_domain                         = Get-EmailDomain $email
            whatsapp_raw                         = [string]$row.whatsapp_raw
            whatsapp_e164                        = $phone
            intencao_viagem_raw                  = ''
            intencao_viagem_label                = ''
            forma_viagem_raw                     = ''
            forma_viagem_label                   = ''
            caminho_interesse_raw                = ''
            caminho_interesse_label              = ''
            mensagem_interesse                   = [string]$row.mensagem_interesse
            consentimento_status                 = [string]$row.consentimento_status
            submitted_at_raw                     = [string]$row.submitted_at_raw
            submitted_at_iso                     = Convert-ExcelDateValue $row.submitted_at_raw
            mapping_status_intencao_viagem       = 'not_applicable'
            mapping_status_forma_viagem          = 'not_applicable'
            mapping_status_caminho_interesse     = 'not_applicable'
        }
    }

    foreach ($row in $contatos2026IBlock3) {
        $name = Get-RowValue -Row $row -Patterns @('Nome:')
        $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('Email:'))
        $phoneRaw = Get-RowValue -Row $row -Patterns @('WhatsApp:')
        $phone = Normalize-Phone $phoneRaw
        $caminho = Get-RowValue -Row $row -Patterns @('Qual o Caminho do seu interesse:')
        $mensagem = Get-RowValue -Row $row -Patterns @('Como podemos ajud*')
        $consentimento = Get-RowValue -Row $row -Patterns @('Termo de uso')
        $submittedRaw = Get-RowValue -Row $row -Patterns @('DATE')
        $leads += [pscustomobject]@{
            lead_id                              = New-PersonKey -Name $name -Email $email -Phone $phoneRaw
            source_file                          = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet                         = 'Contatos 2026 I'
            source_dataset                       = 'contatos_2026_i_bloco_3'
            source_block                         = 'bloco_3'
            record_classification                = 'real_operational'
            lead_legacy_id                       = Get-RowValue -Row $row -Patterns @('ID')
            nome_completo                        = $name
            email                                = $email
            email_domain                         = Get-EmailDomain $email
            whatsapp_raw                         = $phoneRaw
            whatsapp_e164                        = $phone
            intencao_viagem_raw                  = ''
            intencao_viagem_label                = ''
            forma_viagem_raw                     = ''
            forma_viagem_label                   = ''
            caminho_interesse_raw                = $caminho
            caminho_interesse_label              = ''
            mensagem_interesse                   = $mensagem
            consentimento_status                 = $consentimento
            submitted_at_raw                     = $submittedRaw
            submitted_at_iso                     = Convert-ExcelDateValue $submittedRaw
            mapping_status_intencao_viagem       = 'not_applicable'
            mapping_status_forma_viagem          = 'not_applicable'
            mapping_status_caminho_interesse     = 'pending_business_definition'
        }
    }

    $leadOptionMapping = @()
    foreach ($record in $leads) {
        foreach ($fieldName in @('intencao_viagem_raw', 'forma_viagem_raw', 'caminho_interesse_raw')) {
            $rawValue = [string]$record.$fieldName
            if (-not [string]::IsNullOrWhiteSpace($rawValue)) {
                $leadOptionMapping += [pscustomobject]@{
                    source_dataset   = [string]$record.source_dataset
                    field_name       = $fieldName
                    raw_value        = $rawValue
                    semantic_label   = ''
                    mapping_status   = 'pending_business_definition'
                    note             = 'Valor preservado do XLSX original'
                }
            }
        }
    }
    $leadOptionMapping = $leadOptionMapping | Sort-Object field_name, raw_value -Unique

    $customers = @()
    $documents = @()
    $medical = @()

    foreach ($row in $clientesAntigos) {
        $nome = Get-RowValue -Row $row -Patterns @('1.1 Nome Completo')
        $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('1.2 E-mail de Contato'))
        $phoneRaw = Get-RowValue -Row $row -Patterns @('1.3 WhatsApp')
        $phone = Normalize-Phone $phoneRaw
        $personKey = New-PersonKey -Name $nome -Email $email -Phone $phoneRaw
        $address = Get-RowValue -Row $row -Patterns @('1.8 Endere*')
        $location = Split-CityState $address
        $submittedIso = Convert-ExcelDateValue (Get-RowValue -Row $row -Patterns @('Timestamp'))
        $birthDateIso = Convert-ExcelDateValue (Get-RowValue -Row $row -Patterns @('1.4 Data de Nascimento'))
        $prepared = Get-RowValue -Row $row -Patterns @('2.11 Me considero apto para fazer o Caminho.')
        $customers += [pscustomobject]@{
            contact_id                = $personKey
            source_file               = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet              = 'Clientes Antigos'
            source_dataset            = 'clientes_antigos'
            record_classification     = 'real_operational'
            customer_stage            = 'cliente_antigo'
            submitted_at_iso          = $submittedIso
            ano_referencia            = Get-RowValue -Row $row -Patterns @('Ano')
            username                  = Get-RowValue -Row $row -Patterns @('Username')
            nome_completo             = $nome
            email                     = $email
            email_domain              = Get-EmailDomain $email
            whatsapp_raw              = $phoneRaw
            whatsapp_e164             = $phone
            data_nascimento           = $birthDateIso
            birth_year                = Get-BirthYear $birthDateIso
            cidade                    = $location.cidade
            estado                    = $location.estado
            endereco_raw              = $location.endereco_raw
            interesse_roteiro_raw     = Get-RowValue -Row $row -Patterns @('Roteiro tour4Friends de meu interesse.')
            hospedagem_tipo_raw       = ''
            hospedagem_categoria_raw  = ''
            nivel_conhecimento_raw    = ''
            preparado_para_caminho    = $prepared
            lgpd_tier                 = 'restricted_operational'
        }

        $documents += [pscustomobject]@{
            document_id              = (Get-Sha256Hex ("document|" + $personKey + '|clientes_antigos'))
            contact_id               = $personKey
            source_dataset           = 'clientes_antigos'
            document_type            = 'passport_supporting_documents'
            passport_informed        = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('1.6 Passaporte*'))) -eq $false
            passport_copy_present    = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('1.7 Copia do Passaporte*'))) -eq $false
            medical_certificate_present = $false
            status                   = 'normalized_without_raw_values'
        }

        $medical += [pscustomobject]@{
            contact_id                    = $personKey
            source_dataset                = 'clientes_antigos'
            health_note_present           = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('2.2 Algo que queira mencionar*'))) -eq $false
            uses_heart_medicine_flag      = Get-RowValue -Row $row -Patterns @('2.3 Tomo algum rem*')
            joint_problem_flag            = Get-RowValue -Row $row -Patterns @('2.4 Tenho algum problema*')
            preventive_exam_regular       = Get-RowValue -Row $row -Patterns @('2.5 Procuro ir ao m*dico regularmente*')
            training_status               = Get-RowValue -Row $row -Patterns @('2.9 Estou treinando para o Caminho.')
            prepared_for_route            = $prepared
            medical_certificate_present   = $false
        }
    }

    foreach ($row in $contatos2026) {
        $nome = Get-RowValue -Row $row -Patterns @('1.1 Nome e Sobrenome')
        $email = Normalize-Email (Get-RowValue -Row $row -Patterns @('1.2 E-mail de Contato'))
        $phoneRaw = Get-RowValue -Row $row -Patterns @('1.3 WhatsApp')
        $phone = Normalize-Phone $phoneRaw
        $personKey = New-PersonKey -Name $nome -Email $email -Phone $phoneRaw
        $cityStateRaw = Get-RowValue -Row $row -Patterns @('1.8 Cidade * Estado')
        $location = Split-CityState $cityStateRaw
        $submittedIso = Convert-ExcelDateValue (Get-RowValue -Row $row -Patterns @('Timestamp'))
        $birthDateIso = Convert-ExcelDateValue (Get-RowValue -Row $row -Patterns @('1.4 Data de Nascimento'))
        $prepared = Get-RowValue -Row $row -Patterns @('3.11 Preparado para o Caminho')
        $customers += [pscustomobject]@{
            contact_id                = $personKey
            source_file               = 'Cópia de  T4F_mail_marketing.xlsx'
            source_sheet              = 'Contatos 2026'
            source_dataset            = 'contatos_2026'
            record_classification     = 'real_operational'
            customer_stage            = 'contato_2026'
            submitted_at_iso          = $submittedIso
            ano_referencia            = ''
            username                  = ''
            nome_completo             = $nome
            email                     = $email
            email_domain              = Get-EmailDomain $email
            whatsapp_raw              = $phoneRaw
            whatsapp_e164             = $phone
            data_nascimento           = $birthDateIso
            birth_year                = Get-BirthYear $birthDateIso
            cidade                    = $location.cidade
            estado                    = $location.estado
            endereco_raw              = $location.endereco_raw
            interesse_roteiro_raw     = ''
            hospedagem_tipo_raw       = Get-RowValue -Row $row -Patterns @('2.1 Tipo de Hospedagens')
            hospedagem_categoria_raw  = Get-RowValue -Row $row -Patterns @('2.2 Categoria Hospedagens')
            nivel_conhecimento_raw    = Get-RowValue -Row $row -Patterns @('3.2 N*vel de Conhecimento do Caminho')
            preparado_para_caminho    = $prepared
            lgpd_tier                 = 'restricted_operational'
        }

        $documents += [pscustomobject]@{
            document_id                = (Get-Sha256Hex ("document|" + $personKey + '|contatos_2026'))
            contact_id                 = $personKey
            source_dataset             = 'contatos_2026'
            document_type              = 'passport_supporting_documents'
            passport_informed          = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('1.6 Passaporte*'))) -eq $false
            passport_copy_present      = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('1.7 Copia do Passaporte*'))) -eq $false
            medical_certificate_present = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('3.10 Atestado Medico*'))) -eq $false
            status                     = 'normalized_without_raw_values'
        }

        $medical += [pscustomobject]@{
            contact_id                  = $personKey
            source_dataset              = 'contatos_2026'
            health_note_present         = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('3.8 Sobre a sua sa*de'))) -eq $false
            uses_heart_medicine_flag    = ''
            joint_problem_flag          = ''
            preventive_exam_regular     = Get-RowValue -Row $row -Patterns @('3.9 Procuro ir ao m*dico regularmente*')
            training_status             = Get-RowValue -Row $row -Patterns @('3.6 Experi*ncia com Caminhadas: [Treino para Caminho]')
            prepared_for_route          = $prepared
            medical_certificate_present = [string]::IsNullOrWhiteSpace((Get-RowValue -Row $row -Patterns @('3.10 Atestado Medico*'))) -eq $false
        }
    }

    $routesCatalogSeed = @(
        [pscustomobject]@{ route_id = 'caminho_frances_bike'; route_name = 'Caminho Frances de Bicicleta'; segmento = 'Bike'; modalidade = 'Autoguiado / guiado'; catalog_source = 'Bike - Cicloviagem'; status_catalogo = 'seed_from_material_names' }
        [pscustomobject]@{ route_id = 'caminho_portugues_bike'; route_name = 'Caminho Portugues de Bicicleta'; segmento = 'Bike'; modalidade = 'Autoguiado / guiado'; catalog_source = 'Bike - Cicloviagem'; status_catalogo = 'seed_from_material_names' }
        [pscustomobject]@{ route_id = 'caminho_santiago_pe'; route_name = 'Caminho de Santiago a Pe'; segmento = 'Peregrinacao'; modalidade = 'A pe'; catalog_source = 'Caminho Santiago a Pé'; status_catalogo = 'seed_from_material_names' }
        [pscustomobject]@{ route_id = 'caminho_portugues_grupo_2026'; route_name = 'Grupo 2026 Caminho Portugues'; segmento = 'Peregrinacao'; modalidade = 'Grupo'; catalog_source = 'Grupo 2026 Caminho Português'; status_catalogo = 'seed_from_material_names' }
        [pscustomobject]@{ route_id = 'caminho_assis_2026'; route_name = 'Caminho de Assis 2026'; segmento = 'Peregrinacao'; modalidade = 'Grupo'; catalog_source = 'Grupo 2026 Caminho Assis ITALIA'; status_catalogo = 'seed_from_material_names' }
        [pscustomobject]@{ route_id = 'smarttrip_espanha'; route_name = 'SmartTrip Espanha'; segmento = 'Turismo Europa'; modalidade = 'Pacote'; catalog_source = 'Roteiros Turisticos Europa Fora Caminhos'; status_catalogo = 'seed_from_material_names' }
        [pscustomobject]@{ route_id = 'smarttrip_4_paises'; route_name = 'SmartTrip 4 Paises'; segmento = 'Turismo Europa'; modalidade = 'Pacote'; catalog_source = 'Roteiros Turisticos Europa Fora Caminhos'; status_catalogo = 'seed_from_material_names' }
    )

    $consolidatedReference = foreach ($row in $consolidado) {
        [pscustomobject]@{
            nome_organizacao = Get-RowValue -Row $row -Patterns @('Nome/Organi*')
            email            = Normalize-Email (Get-RowValue -Row $row -Patterns @('Email'))
            whatsapp_e164    = Normalize-Phone (Get-RowValue -Row $row -Patterns @('WhatsApp/Telefone'))
            cidade_endereco  = Get-RowValue -Row $row -Patterns @('Cidade/Endere*')
            fonte            = Get-RowValue -Row $row -Patterns @('Fonte')
            source_dataset   = 'contatos_existentes_sp_11'
            record_classification = 'derived'
        }
    }

    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'source_registry.csv') -Records $sourceRegistry
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'partners.csv') -Records $partners
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'leads.csv') -Records $leads
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'lead_option_mapping.csv') -Records $leadOptionMapping
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'customers.csv') -Records $customers
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'documents.csv') -Records ($documents | Sort-Object document_id -Unique)
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'medical_clearance.csv') -Records ($medical | Sort-Object contact_id, source_dataset -Unique)
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'routes_catalog_seed.csv') -Records $routesCatalogSeed
    Export-RestrictedCsv -OutputPath (Join-Path $restrictedOutput 'partner_consolidated_reference.csv') -Records $consolidatedReference

    Write-Host "Export canônico concluido em: $restrictedOutput"
}
finally {
    Close-XlsxWorkbook -Workbook $mailWorkbook
    Close-XlsxWorkbook -Workbook $prospectWorkbook
}
