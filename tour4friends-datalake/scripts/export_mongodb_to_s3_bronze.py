from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TMP_ROOT = PROJECT_ROOT / "tmp"
ENV_FILE = PROJECT_ROOT / ".env"


def parse_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def serialize_mongo_value(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_mongo_value(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_mongo_value(item) for key, item in value.items()}
    return value


def build_output_directory(collection_name: str, execution_time: datetime) -> Path:
    return (
        TMP_ROOT
        / "bronze"
        / collection_name
        / f"ano={execution_time:%Y}"
        / f"mes={execution_time:%m}"
        / f"dia={execution_time:%d}"
    )


def validate_mongodb_connection(client: MongoClient, mongo_uri: str) -> None:
    try:
        client.admin.command("ping")
    except PyMongoError as exc:
        raise ConnectionError(
            "Nao foi possivel conectar ao MongoDB. "
            f"Verifique MONGO_URI, container/servico ativo e acesso de rede. URI atual: {mongo_uri}"
        ) from exc


def write_collection_as_jsonl(
    client: MongoClient,
    database_name: str,
    collection_name: str,
    execution_time: datetime,
) -> tuple[Path, int]:
    output_dir = build_output_directory(collection_name, execution_time)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "part-00001.jsonl"

    document_count = 0
    collection = client[database_name][collection_name]

    with output_file.open("w", encoding="utf-8", newline="\n") as file_handle:
        for document in collection.find({}):
            serialized = serialize_mongo_value(document)
            file_handle.write(json.dumps(serialized, ensure_ascii=False) + "\n")
            document_count += 1

    print(f"{collection_name}: {document_count} documentos exportados para {output_file}.")
    return output_file, document_count


def upload_file_to_s3(file_path: Path, bucket_name: str, object_key: str, region_name: str) -> None:
    import boto3

    s3_client = boto3.client("s3", region_name=region_name)
    s3_client.upload_file(str(file_path), bucket_name, object_key)
    print(f"Upload concluido: s3://{bucket_name}/{object_key}")


def main() -> None:
    load_dotenv(dotenv_path=ENV_FILE)

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGO_DATABASE", "tour4friends")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    bucket_name = os.getenv("S3_BUCKET", "tour4friends-lake-dev")
    upload_to_s3 = parse_bool_env("UPLOAD_TO_S3", default=False)
    execution_time = datetime.now(UTC)

    try:
        with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
            validate_mongodb_connection(client, mongo_uri)

            collection_names = sorted(client[database_name].list_collection_names())
            if not collection_names:
                raise RuntimeError(f"Nenhuma collection encontrada no banco {database_name}.")

            total_documents = 0
            for collection_name in collection_names:
                output_file, document_count = write_collection_as_jsonl(
                    client=client,
                    database_name=database_name,
                    collection_name=collection_name,
                    execution_time=execution_time,
                )
                total_documents += document_count

                if upload_to_s3:
                    relative_key = output_file.relative_to(TMP_ROOT).as_posix()
                    upload_file_to_s3(
                        file_path=output_file,
                        bucket_name=bucket_name,
                        object_key=relative_key,
                        region_name=aws_region,
                    )

        print(
            "Exportacao Bronze finalizada. "
            f"Collections processadas: {len(collection_names)}. "
            f"Total de documentos exportados: {total_documents}."
        )
    except Exception as exc:
        print(f"Erro na exportacao MongoDB -> Bronze: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
