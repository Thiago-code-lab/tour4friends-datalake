from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ENV_FILE = PROJECT_ROOT / ".env"
SUPPORTED_ENCODINGS: tuple[str, ...] = ("utf-8", "latin1")


def parse_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def collection_name_from_path(file_path: Path) -> str:
    normalized_name = re.sub(r"[^a-zA-Z0-9]+", "_", file_path.stem.strip().lower())
    return normalized_name.strip("_")


def find_csv_files(data_dir: Path) -> list[Path]:
    return sorted(path for path in data_dir.glob("*.csv") if path.is_file())


def read_csv_with_fallback(file_path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in SUPPORTED_ENCODINGS:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
        except Exception as exc:
            raise RuntimeError(f"Falha ao ler o CSV {file_path.name}: {exc}") from exc
    raise RuntimeError(f"Falha ao ler {file_path.name} com os encodings suportados.") from last_error


def dataframe_to_documents(dataframe: pd.DataFrame) -> list[dict]:
    sanitized_frame = dataframe.where(pd.notna(dataframe), None)
    return sanitized_frame.to_dict(orient="records")


def reset_collection_if_enabled(collection: Collection, reset_enabled: bool) -> None:
    if reset_enabled:
        collection.delete_many({})


def load_collection(client: MongoClient, database_name: str, csv_file: Path, reset_enabled: bool) -> int:
    dataframe = read_csv_with_fallback(csv_file)
    documents = dataframe_to_documents(dataframe)
    collection_name = collection_name_from_path(csv_file)
    collection = client[database_name][collection_name]

    reset_collection_if_enabled(collection, reset_enabled)

    if not documents:
        print(f"{collection_name}: 0 registros inseridos (arquivo vazio).")
        return 0

    result = collection.insert_many(documents, ordered=False)
    inserted_count = len(result.inserted_ids)
    print(f"{collection_name}: {inserted_count} registros inseridos.")
    return inserted_count


def validate_environment(data_dir: Path, csv_files: Iterable[Path]) -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Pasta de dados nao encontrada: {data_dir}")
    if not data_dir.is_dir():
        raise NotADirectoryError(f"O caminho de dados nao e uma pasta valida: {data_dir}")
    if not list(csv_files):
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em: {data_dir}")


def validate_mongodb_connection(client: MongoClient, mongo_uri: str) -> None:
    try:
        client.admin.command("ping")
    except PyMongoError as exc:
        raise ConnectionError(
            "Nao foi possivel conectar ao MongoDB. "
            f"Verifique MONGO_URI, container/servico ativo e acesso de rede. URI atual: {mongo_uri}"
        ) from exc


def main() -> None:
    load_dotenv(dotenv_path=ENV_FILE)

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGO_DATABASE", "tour4friends")
    reset_enabled = parse_bool_env("RESET_COLLECTIONS", default=False)

    csv_files = find_csv_files(DATA_DIR)
    validate_environment(DATA_DIR, csv_files)

    try:
        with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
            validate_mongodb_connection(client, mongo_uri)

            total_inserted = 0
            for csv_file in csv_files:
                total_inserted += load_collection(client, database_name, csv_file, reset_enabled)

        print(
            "Carga finalizada. "
            f"Collections processadas: {len(csv_files)}. "
            f"Total de registros inseridos: {total_inserted}."
        )
    except Exception as exc:
        print(f"Erro na carga CSV -> MongoDB: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
