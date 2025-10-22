from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from streets_data import generate_street_data
from injector import iniciar_injecao_loop
import requests
from bs4 import BeautifulSoup
import threading
import os

app = Flask(__name__)
ARQUIVO = 'data/usuarios.json'
CORS(app)

@app.route('/api/login', methods=['POST'])
def login():
    dados = request.json
    with open(ARQUIVO) as f:
        usuarios = json.load(f)

    for u in usuarios:
        if u['usuario'] == dados['usuario'] and u['senha'] == dados['senha']:
            return jsonify({'autenticado': True, 'email': u.get('email')}), 200

    return jsonify({'autenticado': False}), 401

@app.route('/api/cadastro', methods=['POST'])
def cadastrar_usuario():
    novo = request.json
    if not novo.get('usuario') or not novo.get('senha'):
        return jsonify({'mensagem': 'Campos obrigatórios'}), 400

    if not os.path.exists(ARQUIVO):
        with open(ARQUIVO, 'w') as f:
            json.dump([], f)

    with open(ARQUIVO, 'r') as f:
        usuarios = json.load(f)

    if any(u['usuario'] == novo['usuario'] for u in usuarios):
        return jsonify({'mensagem': 'Usuário já existe'}), 409

    usuarios.append(novo)

    with open(ARQUIVO, 'w') as f:
        json.dump(usuarios, f, indent=2)

    return jsonify({'mensagem': 'Usuário cadastrado com sucesso'}), 201


@app.route('/api/rua/<nome_rua>', methods=['GET'])
def rua(nome_rua):
    data = generate_street_data(nome_rua)
    if data:
        return jsonify(data)
    return jsonify({"erro": "Rua não encontrada"}), 404

@app.route('/api/historico', methods=['GET'])
def historico_ingestao():
    try:
        with open('data/historico_ingestao.json', 'r') as f:
            historico = json.load(f)
            return jsonify(historico)
    except FileNotFoundError:
        return jsonify({"erro": "Histórico não encontrado"}), 404
    except json.JSONDecodeError:
        return jsonify({"erro": "Erro ao ler histórico"}), 500

@app.route('/api/noticias', methods=['GET'])
def noticias_agua_santo_andre():
    noticias = []

    fontes = [
        {
            "url": "https://portais.santoandre.sp.gov.br/semasa/#:~:text=Campanha%20%E2%80%9CUm%20Dia%20no%20Parque,da%20campanha%20Um%20D",
            "titulo": "Sabesp e Prefeitura agem rápido após rompimento de rede de água",
            "resumo": "Prefeitura e Sabesp atuam para conter vazamento na Perimetral e liberar vias após rompimento de rede de água."
        },

        {
            "url": "https://www.dgabc.com.br/Noticia/4238034/moradores-reclamam-de-falta-d-agua-ha-dois-dias-em-santo-andre",
            "titulo": "Moradores reclamam de falta d'água há dois dias",
            "resumo": "Bairro Jardim Ipanema sofre com desabastecimento prolongado; Sabesp realiza reparos emergenciais.",
        },
        {
            "url": "https://oglobo.globo.com/brasil/noticia/2025/04/04/alagamentos-contencao-item-obrigatorio-em-santo-andre-ja-nao-para-mais-enchentes-com-agua-acima-de-2-metros.ghtml",
            "titulo": "Alagamentos expõem falhas na contenção em Santo André",
            "resumo": "Chuvas intensas superam barreiras e causam perdas materiais; prefeitura promete obras de infraestrutura.",
        },
    ]

    for fonte in fontes:
        noticias.append({
            "titulo": fonte["titulo"],
            "link": fonte["url"],
            "resumo": fonte["resumo"],
            "data": fonte["url"].split("/")[3] if "/202" in fonte["url"] else "2025-10-08"
        })

    return jsonify(noticias)


if __name__ == '__main__':
    threading.Thread(target=iniciar_injecao_loop, daemon=True).start()
    app.run(debug=True)