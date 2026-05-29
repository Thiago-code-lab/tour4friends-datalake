from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRONZE_ROOT = PROJECT_ROOT / "tmp" / "bronze"
SILVER_ROOT = PROJECT_ROOT / "tmp" / "silver"


def validate_bronze_root(bronze_root: Path) -> list[Path]:
    if not bronze_root.exists():
        raise FileNotFoundError(f"Pasta Bronze nao encontrada: {bronze_root}")
    if not bronze_root.is_dir():
        raise NotADirectoryError(f"O caminho Bronze nao e uma pasta valida: {bronze_root}")

    jsonl_files = sorted(path for path in bronze_root.rglob("*.jsonl") if path.is_file())
    if not jsonl_files:
        raise FileNotFoundError(f"Nenhum arquivo JSON Lines encontrado em: {bronze_root}")
    return jsonl_files


def normalize_nested_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def load_jsonl_file(file_path: Path) -> pd.DataFrame:
    records: list[dict[str, Any]] = []

    with file_path.open("r", encoding="utf-8") as file_handle:
        for line_number, raw_line in enumerate(file_handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON invalido em {file_path} na linha {line_number}: {exc}") from exc
            normalized_record = {key: normalize_nested_value(value) for key, value in record.items()}
            records.append(normalized_record)

    if not records:
        return pd.DataFrame()
    return pd.DataFrame.from_records(records)


def build_silver_output_path(jsonl_file: Path) -> Path:
    relative_path = jsonl_file.relative_to(BRONZE_ROOT)
    parquet_relative_path = relative_path.with_suffix(".parquet")
    return SILVER_ROOT / parquet_relative_path


def convert_jsonl_to_parquet(jsonl_file: Path) -> Path:
    dataframe = load_jsonl_file(jsonl_file)
    output_path = build_silver_output_path(jsonl_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_parquet(output_path, engine="pyarrow", index=False)
    return output_path


def main() -> None:
    try:
        jsonl_files = validate_bronze_root(BRONZE_ROOT)
        converted_files = 0

        for jsonl_file in jsonl_files:
            output_path = convert_jsonl_to_parquet(jsonl_file)
            print(f"Convertido: {jsonl_file} -> {output_path}")
            converted_files += 1

        print(
            "Conversao Bronze -> Silver finalizada. "
            f"Arquivos processados: {converted_files}. "
            f"Saida base: {SILVER_ROOT}"
        )
    except Exception as exc:
        print(f"Erro na conversao Bronze -> Silver: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
