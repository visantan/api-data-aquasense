import json
import time
import random
from datetime import datetime
from data.ruas import ruas

ARQUIVO_ATUAL = 'data/last_result.json'
ARQUIVO_HISTORICO = 'data/historico_ingestao.json'

def gerar_status():
    return {
        "vazamento": random.choice([True, False]),
        "obra": random.choice([True, False]),
        "qualidade": random.randint(0, 100),
        "consumo_agua": gerar_consumo_agua()
    }

def gerar_consumo_agua(consumo_anterior=None):
    # print("consumo naterior: ",consumo_anterior)
    if consumo_anterior is None:
        return random.randint(50, 500)
    novo = consumo_anterior + random.randint(-20, 20)
    return max(50, min(500, novo))

def salvar_resultado_atual(dados_por_rua):
    with open(ARQUIVO_ATUAL, 'w') as f:
        json.dump(dados_por_rua, f, indent=2)

def salvar_historico(dado):
    try:
        with open(ARQUIVO_HISTORICO, 'r') as f:
            historico = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historico = []

    historico.append(dado)

    with open(ARQUIVO_HISTORICO, 'w') as f:
        json.dump(historico, f, indent=2)

def gerar_ingestao_completa():
    timestamp = datetime.now().isoformat()
    resultado = {}
    ruas_com_status = []

    try:
        with open(ARQUIVO_ATUAL, 'r') as f:
            ultimo_resultado = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ultimo_resultado = {}

    for rua in ruas:
        id_rua = str(rua["id"])
        anterior = ultimo_resultado.get(id_rua)
        # print("anterior: ",anterior)
        consumo_anterior = anterior["status"]["consumo_agua"] if anterior else None
        # print("consumo naterior: ",consumo_anterior)

        status = {
            "vazamento": random.choice([True, False]),
            "obra": random.choice([True, False]),
            "qualidade": random.randint(0, 100),
            "consumo_agua": gerar_consumo_agua(consumo_anterior)
        }

        resultado[id_rua] = {
            **rua,
            "status": status
        }
        ruas_com_status.append({
            **rua,
            "status": status
        })

    salvar_resultado_atual(resultado)
    salvar_historico({
        "timestamp": timestamp,
        "ruas": ruas_com_status
    })

    print(f"[{timestamp}] Ingestão completa salva com {len(ruas)} ruas.")

def iniciar_injecao_loop():
    while True:
        gerar_ingestao_completa()
        time.sleep(60)