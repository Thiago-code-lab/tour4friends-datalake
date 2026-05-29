from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
BRONZE_ROOT = PROJECT_ROOT / "tmp" / "bronze"
SILVER_ROOT = PROJECT_ROOT / "tmp" / "silver"
GOLD_ROOT = PROJECT_ROOT / "tmp" / "gold"
REQUIRED_GOLD_TABLES: tuple[str, ...] = (
    "gold_receita_por_mes",
    "gold_reservas_por_destino",
    "gold_ticket_medio_por_cliente",
    "gold_taxa_cancelamento",
)
OPTIONAL_GOLD_TABLES: tuple[str, ...] = ("gold_satisfacao_por_destino",)


def print_status(label: str, status: str, detail: str) -> None:
    print(f"[{status}] {label}: {detail}")


def count_mongodb_documents() -> dict[str, int]:
    load_dotenv(dotenv_path=ENV_FILE)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGO_DATABASE", "tour4friends")

    try:
        with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
            client.admin.command("ping")
            collection_names = sorted(client[database_name].list_collection_names())
            if not collection_names:
                raise RuntimeError(f"Nenhuma collection encontrada no banco {database_name}.")

            counts = {
                collection_name: client[database_name][collection_name].count_documents({})
                for collection_name in collection_names
            }
            print_status("MongoDB", "OK", f"{len(collection_names)} collection(s) encontrada(s).")
            return counts
    except (PyMongoError, RuntimeError) as exc:
        raise RuntimeError(f"Falha ao validar collections no MongoDB: {exc}") from exc


def count_jsonl_rows(bronze_root: Path) -> dict[str, int]:
    if not bronze_root.exists() or not bronze_root.is_dir():
        raise FileNotFoundError(f"Pasta Bronze nao encontrada: {bronze_root}")

    counts: dict[str, int] = defaultdict(int)
    jsonl_files = sorted(path for path in bronze_root.rglob("*.jsonl") if path.is_file())
    if not jsonl_files:
        raise FileNotFoundError(f"Nenhum arquivo JSONL encontrado em: {bronze_root}")

    for file_path in jsonl_files:
        relative_parts = file_path.relative_to(bronze_root).parts
        collection_name = relative_parts[0]
        with file_path.open("r", encoding="utf-8") as file_handle:
            counts[collection_name] += sum(1 for line in file_handle if line.strip())

    print_status("Bronze", "OK", f"{len(jsonl_files)} arquivo(s) JSONL encontrado(s).")
    return dict(counts)


def count_parquet_rows(silver_root: Path) -> dict[str, int]:
    if not silver_root.exists() or not silver_root.is_dir():
        raise FileNotFoundError(f"Pasta Silver nao encontrada: {silver_root}")

    counts: dict[str, int] = defaultdict(int)
    parquet_files = sorted(path for path in silver_root.rglob("*.parquet") if path.is_file())
    if not parquet_files:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em: {silver_root}")

    for file_path in parquet_files:
        relative_parts = file_path.relative_to(silver_root).parts
        collection_name = relative_parts[0]
        dataframe = pd.read_parquet(file_path)
        counts[collection_name] += len(dataframe.index)

    print_status("Silver", "OK", f"{len(parquet_files)} arquivo(s) Parquet encontrado(s).")
    return dict(counts)


def count_gold_rows(gold_root: Path) -> dict[str, int]:
    if not gold_root.exists() or not gold_root.is_dir():
        raise FileNotFoundError(f"Pasta Gold nao encontrada: {gold_root}")

    counts: dict[str, int] = defaultdict(int)
    parquet_files = sorted(path for path in gold_root.rglob("*.parquet") if path.is_file())
    if not parquet_files:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em: {gold_root}")

    for file_path in parquet_files:
        relative_parts = file_path.relative_to(gold_root).parts
        table_name = relative_parts[0]
        dataframe = pd.read_parquet(file_path)
        counts[table_name] += len(dataframe.index)

    print_status("Gold", "OK", f"{len(parquet_files)} arquivo(s) Parquet encontrado(s).")
    return dict(counts)


def compare_layers(
    mongodb_counts: dict[str, int],
    bronze_counts: dict[str, int],
    silver_counts: dict[str, int],
) -> bool:
    all_collections = sorted(set(mongodb_counts) | set(bronze_counts) | set(silver_counts))
    print("")
    print("Resumo por collection")
    print("collection | mongodb | bronze_jsonl | silver_parquet | status")

    is_valid = True
    for collection_name in all_collections:
        mongo_count = mongodb_counts.get(collection_name, 0)
        bronze_count = bronze_counts.get(collection_name, 0)
        silver_count = silver_counts.get(collection_name, 0)
        counts_match = mongo_count == bronze_count == silver_count
        status = "OK" if counts_match else "FAIL"
        print(f"{collection_name} | {mongo_count} | {bronze_count} | {silver_count} | {status}")
        if not counts_match:
            is_valid = False

    return is_valid


def validate_gold_tables(gold_counts: dict[str, int]) -> bool:
    print("")
    print("Resumo Gold")
    print("gold_table | rows | status")

    is_valid = True
    for table_name in REQUIRED_GOLD_TABLES:
        row_count = gold_counts.get(table_name, 0)
        status = "OK" if row_count > 0 else "FAIL"
        print(f"{table_name} | {row_count} | {status}")
        if row_count <= 0:
            is_valid = False

    for table_name in OPTIONAL_GOLD_TABLES:
        row_count = gold_counts.get(table_name, 0)
        status = "OK" if row_count > 0 else "SKIP"
        print(f"{table_name} | {row_count} | {status}")

    return is_valid


def main() -> None:
    try:
        mongodb_counts = count_mongodb_documents()
        bronze_counts = count_jsonl_rows(BRONZE_ROOT)
        silver_counts = count_parquet_rows(SILVER_ROOT)
        gold_counts = count_gold_rows(GOLD_ROOT)
        layers_valid = compare_layers(mongodb_counts, bronze_counts, silver_counts)
        gold_valid = validate_gold_tables(gold_counts)
        is_valid = layers_valid and gold_valid

        if is_valid:
            print("")
            print_status("Resultado", "OK", "As contagens entre MongoDB, Bronze, Silver e Gold estao consistentes.")
            return

        print("")
        print_status("Resultado", "FAIL", "Ha divergencias entre as camadas ou faltam tabelas Gold obrigatorias.")
        raise SystemExit(1)
    except Exception as exc:
        print_status("Resultado", "FAIL", str(exc))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
