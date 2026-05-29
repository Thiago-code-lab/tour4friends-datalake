from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


PREFIXES: tuple[str, ...] = ("bronze/", "silver/", "gold/", "logs/", "checkpoints/")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def main() -> None:
    load_dotenv(dotenv_path=ENV_FILE)

    bucket_name = os.getenv("S3_BUCKET", "tour4friends-lake-dev")
    region_name = os.getenv("AWS_REGION", "us-east-1")

    try:
        import boto3

        s3_client = boto3.client("s3", region_name=region_name)

        for prefix in PREFIXES:
            s3_client.put_object(Bucket=bucket_name, Key=prefix)
            print(f"Prefixo criado: s3://{bucket_name}/{prefix}")

        print("Estrutura base do Data Lake criada no bucket.")
    except Exception as exc:
        print(f"Erro ao criar a estrutura base no S3: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
