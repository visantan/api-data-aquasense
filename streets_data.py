import json
import random
import os
from data.ruas import ruas

ARQUIVO = 'data/last_result.json'

def load_last_result():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def generate_consumo_agua():
    return random.randint(50, 500)

def save_last_result(dados_por_rua):
    with open(ARQUIVO, 'w') as f:
        json.dump(dados_por_rua, f, indent=2)

def generate_new_quality(qualidade_anterior):
    if qualidade_anterior is None:
        return random.randint(0, 100)
    novo = qualidade_anterior + random.randint(-3, 3)
    return max(0, min(100, novo))

def generate_street_data(nome_rua):
    rua = next((r for r in ruas if r["nome"].lower() == nome_rua.lower()), None)
    if not rua:
        return None

    resultados = load_last_result()
    id_rua = str(rua["id"])
    anterior = resultados.get(id_rua)

    qualidade_anterior = anterior["status"]["qualidade"] if anterior else None
    nova_qualidade = generate_new_quality(qualidade_anterior)

    novo_status = {
    "vazamento": anterior["status"]["vazamento"] if anterior else random.choice([True, False]),
    "obra": anterior["status"]["obra"] if anterior else random.choice([True, False]),
    "qualidade": nova_qualidade,
    "consumo_agua": generate_consumo_agua()
    }

    resultado = {
        **rua,
        "status": novo_status
    }

    resultados[id_rua] = resultado
    save_last_result(resultados)
    return resultado