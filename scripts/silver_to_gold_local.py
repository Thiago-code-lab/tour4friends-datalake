from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SILVER_ROOT = PROJECT_ROOT / "tmp" / "silver"
GOLD_ROOT = PROJECT_ROOT / "tmp" / "gold"
REQUIRED_GOLD_TABLES: tuple[str, ...] = (
    "gold_receita_por_mes",
    "gold_reservas_por_destino",
    "gold_ticket_medio_por_cliente",
    "gold_taxa_cancelamento",
)


def print_status(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def read_collection_from_silver(collection_name: str) -> pd.DataFrame:
    collection_root = SILVER_ROOT / collection_name
    if not collection_root.exists() or not collection_root.is_dir():
        raise FileNotFoundError(f"Collection Silver nao encontrada: {collection_root}")

    parquet_files = sorted(path for path in collection_root.rglob("*.parquet") if path.is_file())
    if not parquet_files:
        raise FileNotFoundError(f"Nenhum Parquet encontrado para a collection {collection_name}.")

    frames = [pd.read_parquet(file_path) for file_path in parquet_files]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def require_columns(dataframe: pd.DataFrame, table_name: str, required_columns: set[str]) -> bool:
    missing_columns = sorted(column for column in required_columns if column not in dataframe.columns)
    if missing_columns:
        print_status(
            "WARN",
            f"{table_name} ignorada. Colunas ausentes: {', '.join(missing_columns)}",
        )
        return False
    return True


def write_gold_table(table_name: str, dataframe: pd.DataFrame) -> None:
    output_dir = GOLD_ROOT / table_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "part-00001.parquet"
    dataframe.to_parquet(output_file, engine="pyarrow", index=False)
    print_status("OK", f"{table_name} gerada em {output_file} com {len(dataframe.index)} linha(s).")


def coerce_numeric(series: pd.Series) -> pd.Series:
    normalized = (
        series.astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    normalized = normalized.replace({"": None, "nan": None, "None": None})
    return pd.to_numeric(normalized, errors="coerce")


def parse_date_column(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def build_receita_por_mes(reservas_df: pd.DataFrame) -> pd.DataFrame | None:
    table_name = "gold_receita_por_mes"
    if not require_columns(reservas_df, table_name, {"data_reserva", "valor_total_R$"}):
        return None

    dataframe = reservas_df.loc[:, ["data_reserva", "valor_total_R$"]].copy()
    dataframe["data_reserva"] = parse_date_column(dataframe["data_reserva"])
    dataframe["valor_total"] = coerce_numeric(dataframe["valor_total_R$"])
    dataframe = dataframe.dropna(subset=["data_reserva", "valor_total"])
    if dataframe.empty:
        print_status("WARN", f"{table_name} ignorada. Nao ha linhas validas apos o tratamento.")
        return None

    dataframe["mes_referencia"] = dataframe["data_reserva"].dt.to_period("M").astype(str)
    aggregated = (
        dataframe.groupby("mes_referencia", as_index=False)
        .agg(receita_total=("valor_total", "sum"), quantidade_reservas=("valor_total", "size"))
        .sort_values("mes_referencia")
    )
    return aggregated


def build_reservas_por_destino(reservas_df: pd.DataFrame) -> pd.DataFrame | None:
    table_name = "gold_reservas_por_destino"
    if not require_columns(reservas_df, table_name, {"roteiro"}):
        return None

    dataframe = reservas_df.copy()
    if "valor_total_R$" in dataframe.columns:
        dataframe["valor_total"] = coerce_numeric(dataframe["valor_total_R$"])
    if "n_pessoas" in dataframe.columns:
        dataframe["n_pessoas"] = pd.to_numeric(dataframe["n_pessoas"], errors="coerce")

    aggregations: dict[str, tuple[str, str]] = {"quantidade_reservas": ("roteiro", "size")}
    if "n_pessoas" in dataframe.columns:
        aggregations["total_pessoas"] = ("n_pessoas", "sum")
    if "valor_total" in dataframe.columns:
        aggregations["receita_total"] = ("valor_total", "sum")

    aggregated = dataframe.groupby("roteiro", as_index=False).agg(**aggregations).sort_values("roteiro")
    return aggregated


def build_ticket_medio_por_cliente(reservas_df: pd.DataFrame) -> pd.DataFrame | None:
    table_name = "gold_ticket_medio_por_cliente"
    if not require_columns(reservas_df, table_name, {"id_cliente", "valor_total_R$"}):
        return None

    dataframe = reservas_df.loc[:, ["id_cliente", "valor_total_R$"]].copy()
    dataframe["valor_total"] = coerce_numeric(dataframe["valor_total_R$"])
    dataframe = dataframe.dropna(subset=["id_cliente", "valor_total"])
    if dataframe.empty:
        print_status("WARN", f"{table_name} ignorada. Nao ha linhas validas apos o tratamento.")
        return None

    aggregated = (
        dataframe.groupby("id_cliente", as_index=False)
        .agg(ticket_medio=("valor_total", "mean"), quantidade_reservas=("valor_total", "size"))
        .sort_values("id_cliente")
    )
    return aggregated


def build_taxa_cancelamento(reservas_df: pd.DataFrame) -> pd.DataFrame | None:
    table_name = "gold_taxa_cancelamento"
    if not require_columns(reservas_df, table_name, {"status"}):
        return None

    dataframe = reservas_df.copy()
    if "data_reserva" in dataframe.columns:
        dataframe["data_reserva"] = parse_date_column(dataframe["data_reserva"])
        dataframe["mes_referencia"] = dataframe["data_reserva"].dt.to_period("M").astype(str)
        dataframe["mes_referencia"] = dataframe["mes_referencia"].fillna("sem_data")
    else:
        dataframe["mes_referencia"] = "geral"

    status_normalized = dataframe["status"].astype(str).str.strip().str.lower()
    dataframe["reserva_cancelada"] = status_normalized.str.contains("cancel")

    aggregated = (
        dataframe.groupby("mes_referencia", as_index=False)
        .agg(
            total_reservas=("status", "size"),
            reservas_canceladas=("reserva_cancelada", "sum"),
        )
        .sort_values("mes_referencia")
    )
    aggregated["taxa_cancelamento_pct"] = (
        aggregated["reservas_canceladas"] / aggregated["total_reservas"]
    ).fillna(0.0) * 100.0
    return aggregated


def build_satisfacao_por_destino(
    reservas_df: pd.DataFrame,
    satisfacao_df: pd.DataFrame,
) -> pd.DataFrame | None:
    table_name = "gold_satisfacao_por_destino"
    if not require_columns(reservas_df, table_name, {"id_reserva", "roteiro"}):
        return None
    if not require_columns(
        satisfacao_df,
        table_name,
        {"id_reserva", "nota_roteiro", "nota_logistica", "nota_atendimento"},
    ):
        return None

    merged = satisfacao_df.merge(
        reservas_df.loc[:, ["id_reserva", "roteiro"]],
        on="id_reserva",
        how="inner",
    )
    if merged.empty:
        print_status("WARN", f"{table_name} ignorada. Nao ha dados suficientes para o join por id_reserva.")
        return None

    for column in ("nota_roteiro", "nota_logistica", "nota_atendimento"):
        merged[column] = pd.to_numeric(merged[column], errors="coerce")

    merged = merged.dropna(subset=["roteiro", "nota_roteiro", "nota_logistica", "nota_atendimento"])
    if merged.empty:
        print_status("WARN", f"{table_name} ignorada. Nao ha notas validas apos o tratamento.")
        return None

    aggregated = (
        merged.groupby("roteiro", as_index=False)
        .agg(
            quantidade_avaliacoes=("id_reserva", "size"),
            media_nota_roteiro=("nota_roteiro", "mean"),
            media_nota_logistica=("nota_logistica", "mean"),
            media_nota_atendimento=("nota_atendimento", "mean"),
        )
        .sort_values("roteiro")
    )
    return aggregated


def generate_table(
    builder: Callable[[], pd.DataFrame | None],
    table_name: str,
    generated_tables: list[str],
) -> None:
    try:
        dataframe = builder()
    except Exception as exc:
        print_status("WARN", f"{table_name} falhou durante a geracao: {exc}")
        return

    if dataframe is None:
        return

    write_gold_table(table_name, dataframe)
    generated_tables.append(table_name)


def main() -> None:
    try:
        reservas_df = read_collection_from_silver("reservas_viagens_expandido")
    except Exception as exc:
        print_status("FAIL", f"Nao foi possivel carregar reservas_viagens_expandido da Silver: {exc}")
        raise SystemExit(1) from exc

    try:
        satisfacao_df = read_collection_from_silver("satisfacao_clientes_expandido")
    except Exception as exc:
        print_status("WARN", f"satisfacao_clientes_expandido indisponivel para Gold de satisfacao: {exc}")
        satisfacao_df = pd.DataFrame()

    generated_tables: list[str] = []

    generate_table(lambda: build_receita_por_mes(reservas_df), "gold_receita_por_mes", generated_tables)
    generate_table(lambda: build_reservas_por_destino(reservas_df), "gold_reservas_por_destino", generated_tables)
    generate_table(
        lambda: build_ticket_medio_por_cliente(reservas_df),
        "gold_ticket_medio_por_cliente",
        generated_tables,
    )
    generate_table(lambda: build_taxa_cancelamento(reservas_df), "gold_taxa_cancelamento", generated_tables)
    generate_table(
        lambda: build_satisfacao_por_destino(reservas_df, satisfacao_df),
        "gold_satisfacao_por_destino",
        generated_tables,
    )

    missing_required = [table_name for table_name in REQUIRED_GOLD_TABLES if table_name not in generated_tables]
    if missing_required:
        print_status("WARN", f"Tabelas Gold obrigatorias nao geradas: {', '.join(missing_required)}")

    if not generated_tables:
        print_status("FAIL", "Nenhuma tabela Gold foi gerada.")
        raise SystemExit(1)

    print_status("OK", f"Etapa Silver -> Gold finalizada. Tabelas geradas: {', '.join(generated_tables)}")


if __name__ == "__main__":
    main()
