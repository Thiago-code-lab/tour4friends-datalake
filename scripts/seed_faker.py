# scripts/seed_faker.py
import random
from datetime import timedelta
from faker import Faker
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

fake = Faker("pt_BR")
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("MONGO_DB", "tour4friends")]

# ── Listas baseadas nos valores reais do CSV ──────────────────────────────────
MODALIDADES    = ["autoguiado", "guiado", "grupo"]
HOSPEDAGENS    = ["Standard", "Superior"]
MOTIVACOES     = ["Aventura", "Espiritual", "Cultural", "Auto-conhecimento"]
PROFISSOES     = ["Professor", "Vendedor", "Enfermeiro", "Nutricionista",
                  "Motorista", "Advogado", "Contador", "Economista",
                  "Farmacêutico", "Designer", "Arquiteto", "Psicólogo",
                  "Atendente", "Auxiliar administrativo", "Cientista de dados",
                  "Técnico de informática", "Astrônomo"]
CIDADES        = ["São Paulo", "Rio de Janeiro", "Fortaleza", "Salvador",
                  "Manaus", "Curitiba", "Recife", "Porto Alegre", "Belém",
                  "Goiânia", "Campinas", "São Gonçalo", "Duque de Caxias",
                  "Brasília", "Guarulhos", "São Luís", "Jaboatão",
                  "Campo Grande", "Belo Horizonte"]

def gerar_reserva(id_cliente: int) -> dict:
    nome  = fake.first_name()
    sobre = fake.last_name()
    
    data_inicio = fake.date_between(start_date="-8y", end_date="+2y")
    dias        = 17  # fixo no CSV real
    data_fim    = data_inicio + timedelta(days=dias)
    
    valor_orcado = round(random.uniform(1800, 2600), 2)
    fator        = round(random.uniform(0.97, 1.40), 2)
    valor_real   = round(valor_orcado * fator, 2)

    return {
        "id_cliente":         id_cliente,
        "nome_sobrenome":     f"{nome} {sobre}",
        "nome":               nome,
        "sobrenome":          sobre,
        "email":              fake.email(),
        "sexo":               random.choice(["Male", "Female"]),
        "idade":              random.randint(20, 75),
        "cidade_cliente_nome": random.choice(CIDADES),
        "profissao_nome":     random.choice(PROFISSOES),
        "modalidade":         random.choice(MODALIDADES),
        "altura":             round(random.uniform(1.55, 2.10), 2),
        "peso":               round(random.uniform(55.0, 120.0), 1),
        "tipo_roteiro_nome":  "A pe",
        "cidade_inicio":      "Astorga",
        "dias_roteiro":       dias,
        "etapas_roteiro":     12,
        "data_inicio_roteiro": data_inicio.strftime("%d/%m/%Y"),
        "data_final_roteiro":  data_fim.strftime("%d/%m/%Y"),
        "valor_orcado":       valor_orcado,
        "fator_variacao":     fator,
        "valor_real":         valor_real,
        "tipo_hospedagem":    random.choice(HOSPEDAGENS),
        "acompanhantes":      random.randint(1, 10),
        "transporte_inicio":  random.choice(["sim", "não"]),
        "transporte_final":   random.choice(["sim", "não"]),
        "transporte_mochila": random.choice(["sim", "não"]),
        "tour_santiago":      random.choice(["sim", "não"]),
        "motivacao":          random.choice(MOTIVACOES),
    }

def seed(qtd: int = 300):
    collection = db["reservas"]
    collection.drop()  # limpa antes de reinserir (útil para re-rodar)
    
    docs = [gerar_reserva(i) for i in range(1, qtd + 1)]
    result = collection.insert_many(docs)
    
    print(f"✅  {len(result.inserted_ids)} documentos inseridos em 'tour4friends.reservas'")

if __name__ == "__main__":
    seed(300)