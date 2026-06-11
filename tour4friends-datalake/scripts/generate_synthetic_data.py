from __future__ import annotations

import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

RESERVAS_FILE = "reservas_viagens_expandido.csv"
CLIENTES_FILE = "clientes_expandido.csv"
CUSTOS_FILE = "custos_operacionais_expandido.csv"
FUNIL_FILE = "funil_vendas.csv"
SATISFACAO_FILE = "satisfacao_clientes_expandido.csv"
MARKETING_FILE = "investimento_marketing_completo.csv"

TOTAL_RESERVAS = 100_000
TOTAL_CLIENTES = 30_000
TOTAL_LEADS = 180_000
SATISFACAO_RATE = 0.72
SEED = 42

ROTEIROS: dict[str, dict[str, float]] = {
    "Caminho Francês": {"base": 9100.0, "daily_cost": 330.0},
    "Caminho Português": {"base": 6800.0, "daily_cost": 280.0},
    "Caminho do Norte": {"base": 7900.0, "daily_cost": 295.0},
    "Via Francigena": {"base": 8600.0, "daily_cost": 310.0},
    "Caminho Primitivo": {"base": 8300.0, "daily_cost": 305.0},
}

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

CANAIS = ["Instagram", "Google", "Indicação", "YouTube", "Facebook", "TikTok", "WhatsApp"]
MODALIDADES = ["Guiado", "Autoguiado", "Premium"]
STATUS_RESERVA = ["Concluída", "Concluída", "Concluída", "Cancelada", "Reagendada"]
STATUS_FUNIL = ["Fechado", "Negociando", "Sem resposta", "Perdido"]
DESVIOS = ["Hospedagem", "Transporte", "Alimentação", "Guias", "Taxas", "Seguro"]


def ensure_data_dir() -> None:
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        raise FileNotFoundError(f"Pasta de dados não encontrada: {DATA_DIR}")


def random_dates(start: date, end: date, count: int, rng: random.Random) -> list[date]:
    span_days = (end - start).days
    return [start + timedelta(days=rng.randint(0, span_days)) for _ in range(count)]


def generate_clientes(fake: Faker, rng: random.Random) -> pd.DataFrame:
    registros: list[dict[str, object]] = []
    start = date(2020, 1, 1)
    end = date(2026, 12, 31)
    contato_datas = random_dates(start, end, TOTAL_CLIENTES, rng)

    for index in range(1, TOTAL_CLIENTES + 1):
        primeiro_contato = contato_datas[index - 1]
        idade = rng.randint(22, 74)
        qtd_reservas = rng.randint(1, 8)
        ticket_base = rng.randint(6500, 14500)
        total_gasto = int(ticket_base * qtd_reservas * rng.uniform(0.92, 1.35))

        registros.append(
            {
                "id_cliente": f"CLI{index:06d}",
                "nome": fake.name(),
                "idade": idade,
                "cidade_origem": fake.city(),
                "data_primeiro_contact": primeiro_contato.isoformat(),
                "qtd_reservas": qtd_reservas,
                "total_gasto_R$": total_gasto,
                "ultima_viagem": (primeiro_contato + timedelta(days=rng.randint(60, 2200))).isoformat(),
            }
        )

    return pd.DataFrame.from_records(registros)


def generate_reservas(client_ids: list[str], rng: random.Random) -> pd.DataFrame:
    start = date(2020, 1, 1)
    end = date(2026, 12, 31)
    reserva_datas = random_dates(start, end, TOTAL_RESERVAS, rng)

    registros: list[dict[str, object]] = []
    roteiros = list(ROTEIROS.keys())

    for index in range(1, TOTAL_RESERVAS + 1):
        data_reserva = reserva_datas[index - 1]
        roteiro = rng.choice(roteiros)
        modalidade = rng.choice(MODALIDADES)
        n_pessoas = rng.choices([1, 2, 3, 4, 5, 6], weights=[18, 40, 20, 13, 6, 3], k=1)[0]

        perfil = ROTEIROS[roteiro]
        premium_factor = 1.24 if modalidade == "Premium" else (1.06 if modalidade == "Guiado" else 0.88)
        sazonalidade = 1.14 if data_reserva.month in {6, 7, 8, 12} else 0.93 if data_reserva.month in {2, 3} else 1.0
        dias = rng.randint(7, 25)
        valor_total = int((perfil["base"] + perfil["daily_cost"] * dias) * n_pessoas * premium_factor * sazonalidade)

        margem = rng.uniform(0.58, 0.78)
        custo_operacional = int(valor_total * margem)

        registros.append(
            {
                "id_reserva": f"RES{index:06d}",
                "data_reserva": data_reserva.isoformat(),
                "id_cliente": rng.choice(client_ids),
                "roteiro": roteiro,
                "modalidade": modalidade,
                "n_pessoas": n_pessoas,
                "mes_viagem": MESES_PT[data_reserva.month - 1],
                "valor_total_R$": valor_total,
                "custo_operacional_R$": custo_operacional,
                "canal_origem": rng.choice(CANAIS),
                "status": rng.choices(STATUS_RESERVA, weights=[70, 10, 8, 7, 5], k=1)[0],
            }
        )

    return pd.DataFrame.from_records(registros)


def generate_custos(reservas_df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    custo_estimado = (reservas_df["custo_operacional_R$"] * pd.Series([rng.uniform(0.9, 1.08) for _ in range(len(reservas_df))])).round(0).astype(int)
    custo_real = reservas_df["custo_operacional_R$"].astype(int)
    diferenca = custo_real - custo_estimado

    return pd.DataFrame(
        {
            "id_reserva": reservas_df["id_reserva"],
            "roteiro": reservas_df["roteiro"],
            "n_pessoas": reservas_df["n_pessoas"],
            "custo_estimado_R$": custo_estimado,
            "custo_real_R$": custo_real,
            "diferenca_R$": diferenca,
            "item_maior_desvio": [rng.choice(DESVIOS) for _ in range(len(reservas_df))],
            "valor_desvio_R$": (diferenca * pd.Series([rng.uniform(0.6, 1.25) for _ in range(len(reservas_df))])).round(0).astype(int),
        }
    )


def generate_satisfacao(reservas_df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    concluidas = reservas_df.loc[reservas_df["status"] == "Concluída", ["id_reserva", "id_cliente", "modalidade"]].copy()
    quantidade = min(int(TOTAL_RESERVAS * SATISFACAO_RATE), len(concluidas))
    amostra = concluidas.sample(n=quantidade, random_state=SEED).reset_index(drop=True)

    notas_base = amostra["modalidade"].map({"Premium": 9.2, "Guiado": 8.6, "Autoguiado": 8.0}).fillna(8.3)
    roteiro = (notas_base + pd.Series([rng.uniform(-1.8, 0.8) for _ in range(quantidade)])).clip(1, 10).round().astype(int)
    logistica = (notas_base + pd.Series([rng.uniform(-2.0, 0.9) for _ in range(quantidade)])).clip(1, 10).round().astype(int)
    atendimento = (notas_base + pd.Series([rng.uniform(-1.4, 1.0) for _ in range(quantidade)])).clip(1, 10).round().astype(int)
    media = (roteiro + logistica + atendimento) / 3

    comentarios = [
        "Experiência excelente",
        "Boa organização",
        "Roteiro bem estruturado",
        "Hospedagem confortável",
        "Atendimento rápido",
        "Poderia melhorar traslados",
    ]

    return pd.DataFrame(
        {
            "id_reserva": amostra["id_reserva"],
            "id_cliente": amostra["id_cliente"],
            "nota_roteiro": roteiro,
            "nota_logistica": logistica,
            "nota_atendimento": atendimento,
            "comentario": [rng.choice(comentarios) for _ in range(quantidade)],
            "recomenda_empresa": ["Sim" if score >= 7.5 else "Não" for score in media],
        }
    )


def generate_funil(reservas_df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    start = date(2020, 1, 1)
    end = date(2026, 12, 31)
    contatos = random_dates(start, end, TOTAL_LEADS, rng)
    roteiros = list(ROTEIROS.keys())

    registros: list[dict[str, object]] = []
    for index in range(1, TOTAL_LEADS + 1):
        contato = contatos[index - 1]
        status = rng.choices(STATUS_FUNIL, weights=[24, 37, 21, 18], k=1)[0]
        roteiro = rng.choice(roteiros)
        modalidade = rng.choice(MODALIDADES)
        n_pessoas = rng.choices([1, 2, 3, 4, 5], weights=[28, 38, 18, 10, 6], k=1)[0]

        base = ROTEIROS[roteiro]["base"]
        orcamento = int((base * n_pessoas) * (1.06 if modalidade != "Autoguiado" else 0.9) * rng.uniform(0.85, 1.35))

        dias = ""
        data_fechamento = ""
        valor_venda = ""
        if status == "Fechado":
            dias_fechamento = rng.randint(2, 35)
            fechamento = contato + timedelta(days=dias_fechamento)
            if fechamento > end:
                fechamento = end
            dias = str((fechamento - contato).days)
            data_fechamento = fechamento.isoformat()
            valor_venda = f"R$ {int(orcamento * rng.uniform(0.92, 1.12)):,.0f}".replace(",", ".")

        registros.append(
            {
                "id_lead": f"{index:06d}",
                "data_primeiro_contato": contato.isoformat(),
                "origem": rng.choice(CANAIS),
                "roteiro_interesse": roteiro,
                "modalidade": modalidade,
                "n_pessoas": n_pessoas,
                "mes_viagem_desejado": MESES_PT[rng.randint(0, 11)],
                "orcamento_aprox": f"R$ {orcamento:,.0f}".replace(",", "."),
                "status": status,
                "data_fechamento": data_fechamento,
                "dias_ate_fechar": dias,
                "valor_venda": valor_venda,
            }
        )

    return pd.DataFrame.from_records(registros)


def generate_marketing() -> pd.DataFrame:
    meses = pd.period_range(start="2020-01", end="2026-12", freq="M")
    records: list[dict[str, object]] = []

    for idx, periodo in enumerate(meses, start=1):
        fator = 1 + (idx / len(meses)) * 0.45
        google = int(2400 * fator)
        instagram = int(1900 * fator)
        youtube = int(1300 * fator)
        facebook = int(900 * fator)
        outros = int(500 * fator)
        total = google + instagram + youtube + facebook + outros
        leads = int(total / 34)
        vendas = int(leads * 0.09)
        cpc = round(total / max(leads, 1), 2)

        records.append(
            {
                "Mês/Ano": periodo.strftime("%b/%y"),
                "Google_Ads_R$": google,
                "Instagram_Ads_R$": instagram,
                "YouTube_Ads_R$": youtube,
                "Facebook_Ads_R$": facebook,
                "Outros_R$": outros,
                "Total_Investido_R$": total,
                "Leads_Gerados": leads,
                "Vendas_Efetivadas": vendas,
                "CPC_Médio_R$": cpc,
            }
        )

    return pd.DataFrame.from_records(records)


def save_csv(df: pd.DataFrame, filename: str) -> None:
    destination = DATA_DIR / filename
    df.to_csv(destination, index=False, encoding="utf-8")


def main() -> None:
    rng = random.Random(SEED)
    Faker.seed(SEED)
    fake = Faker("pt_BR")

    try:
        ensure_data_dir()

        clientes_df = generate_clientes(fake, rng)
        reservas_df = generate_reservas(clientes_df["id_cliente"].tolist(), rng)
        custos_df = generate_custos(reservas_df, rng)
        satisfacao_df = generate_satisfacao(reservas_df, rng)
        funil_df = generate_funil(reservas_df, rng)
        marketing_df = generate_marketing()

        save_csv(clientes_df, CLIENTES_FILE)
        save_csv(reservas_df, RESERVAS_FILE)
        save_csv(custos_df, CUSTOS_FILE)
        save_csv(funil_df, FUNIL_FILE)
        save_csv(satisfacao_df, SATISFACAO_FILE)
        save_csv(marketing_df, MARKETING_FILE)

        print("Geração concluída com sucesso.")
        print(f"- {RESERVAS_FILE}: {len(reservas_df)}")
        print(f"- {CLIENTES_FILE}: {len(clientes_df)}")
        print(f"- {CUSTOS_FILE}: {len(custos_df)}")
        print(f"- {FUNIL_FILE}: {len(funil_df)}")
        print(f"- {SATISFACAO_FILE}: {len(satisfacao_df)}")
        print(f"- {MARKETING_FILE}: {len(marketing_df)}")
    except Exception as exc:
        print(f"Erro ao gerar dados sintéticos: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
