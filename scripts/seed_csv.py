# scripts/seed_csv.py
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("MONGO_DB", "tour4friends")]

# Lê o CSV da pasta data
df = pd.read_csv("data/tour4friends_csv.csv", sep=";", encoding="utf-8-sig")
df.columns = df.columns.str.strip()

registros = df.to_dict(orient="records")

# Limpa a collection reservas_real se já existir, e insere os novos dados
db["reservas_real"].drop()
db["reservas_real"].insert_many(registros)

print(f"✅  {len(registros)} registros do CSV inseridos em 'reservas_real'")