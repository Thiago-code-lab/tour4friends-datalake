from __future__ import annotations

import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
DATA_DIR = PROJECT_ROOT / "data"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

PACKAGE_IMPORT_HINTS: dict[str, str] = {
    "python-dotenv": "dotenv",
}


def print_status(label: str, status: str, detail: str) -> None:
    print(f"[{status}] {label}: {detail}")


def check_python() -> bool:
    version_info = sys.version_info
    is_valid = version_info >= (3, 10)
    detail = f"{sys.executable} | version {sys.version.split()[0]}"
    print_status("Python", "OK" if is_valid else "FAIL", detail)
    return is_valid


def read_requirements(requirements_file: Path) -> list[str]:
    if not requirements_file.exists():
        raise FileNotFoundError(f"Arquivo requirements.txt nao encontrado: {requirements_file}")

    packages: list[str] = []
    for line in requirements_file.read_text(encoding="utf-8").splitlines():
        package = line.strip()
        if package and not package.startswith("#"):
            packages.append(package)
    return packages


def check_requirements() -> bool:
    try:
        packages = read_requirements(REQUIREMENTS_FILE)
    except Exception as exc:
        print_status("Dependencias", "FAIL", str(exc))
        return False

    missing_packages: list[str] = []
    installed_packages: list[str] = []

    for package in packages:
        try:
            installed_version = version(package)
            installed_packages.append(f"{package}=={installed_version}")
        except PackageNotFoundError:
            missing_packages.append(package)

    if missing_packages:
        print_status("Dependencias", "FAIL", f"Pacotes ausentes: {', '.join(missing_packages)}")
        return False

    print_status("Dependencias", "OK", f"{len(installed_packages)} pacotes instalados.")
    return True


def check_env_file() -> bool:
    if not ENV_FILE.exists():
        print_status("Arquivo .env", "FAIL", f"Arquivo nao encontrado em {ENV_FILE}")
        return False
    print_status("Arquivo .env", "OK", f"Arquivo encontrado em {ENV_FILE}")
    return True


def check_data_dir() -> tuple[bool, int]:
    if not DATA_DIR.exists():
        print_status("Pasta data", "FAIL", f"Pasta nao encontrada em {DATA_DIR}")
        return False, 0
    if not DATA_DIR.is_dir():
        print_status("Pasta data", "FAIL", f"Caminho nao e uma pasta valida: {DATA_DIR}")
        return False, 0

    csv_count = len(sorted(DATA_DIR.glob("*.csv")))
    if csv_count == 0:
        print_status("CSVs", "FAIL", "Nenhum arquivo CSV encontrado.")
        return False, 0

    print_status("Pasta data", "OK", str(DATA_DIR))
    print_status("CSVs", "OK", f"{csv_count} arquivo(s) CSV encontrado(s).")
    return True, csv_count


def check_docker() -> bool:
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        server_version = result.stdout.strip() or "versao do servidor indisponivel"
        print_status("Docker", "OK", f"Daemon acessivel. Server version: {server_version}")
        return True
    except FileNotFoundError:
        print_status("Docker", "FAIL", "Comando docker nao encontrado no PATH.")
        return False
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or "Docker nao respondeu corretamente."
        print_status("Docker", "FAIL", detail)
        return False


def check_mongodb() -> bool:
    load_dotenv(dotenv_path=ENV_FILE)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    try:
        with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
            client.admin.command("ping")
        print_status("MongoDB", "OK", f"Ping concluido com sucesso em {mongo_uri}")
        return True
    except PyMongoError as exc:
        print_status("MongoDB", "FAIL", f"Falha no ping em {mongo_uri}: {exc}")
        return False


def main() -> None:
    checks: list[bool] = []

    checks.append(check_python())
    checks.append(check_requirements())
    checks.append(check_env_file())
    data_ok, _csv_count = check_data_dir()
    checks.append(data_ok)
    checks.append(check_docker())
    checks.append(check_mongodb())

    if all(checks):
        print_status("Resultado", "OK", "Ambiente validado com sucesso.")
        return

    print_status("Resultado", "FAIL", "Uma ou mais validacoes falharam.")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
