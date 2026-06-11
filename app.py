from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from bson.objectid import ObjectId
import database as db 
import rpa 
import google.generativeai as genai

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

genai.configure(api_key="")

modelo_texto = None
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        modelo_texto = m.name
        break

if modelo_texto:
    print(f"Modelo de IA carregado com sucesso: {modelo_texto}")
    ia_model = genai.GenerativeModel(modelo_texto)
else:
    print("Erro: Nenhum modelo de IA encontrado para esta chave.")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/vagas', methods=['POST'])
def criar_vaga():
    dados = request.json
    nova_vaga = {
        "titulo": dados.get("titulo"),
        "descricao": dados.get("descricao"),
        "area": dados.get("area"),
        "salario": dados.get("salario"),
        "modalidade": dados.get("modalidade")
    }
    resultado = db.vagas_collection.insert_one(nova_vaga)
    return jsonify({"mensagem": "Vaga criada!", "id": str(resultado.inserted_id)}), 201

@app.route('/api/vagas', methods=['GET'])
def listar_vagas():
    filtro = {}
    area = request.args.get('area')
    modalidade = request.args.get('modalidade')
    
    if area:
        filtro['area'] = {"$regex": area, "$options": "i"}
    if modalidade:
        filtro['modalidade'] = {"$regex": modalidade, "$options": "i"}

    vagas_cursor = db.vagas_collection.find(filtro)
    vagas_lista = []
    for vaga in vagas_cursor:
        vaga['_id'] = str(vaga['_id'])
        vagas_lista.append(vaga)
    return jsonify(vagas_lista), 200

@app.route('/api/vagas/<id_vaga>', methods=['PUT'])
def atualizar_vaga(id_vaga):
    dados = request.json
    resultado = db.vagas_collection.update_one(
        {"_id": ObjectId(id_vaga)}, 
        {"$set": dados}
    )
    if resultado.matched_count > 0:
        return jsonify({"mensagem": "Vaga atualizada com sucesso!"}), 200
    return jsonify({"erro": "Vaga não encontrada"}), 404

@app.route('/api/vagas/<id_vaga>', methods=['DELETE'])
def deletar_vaga(id_vaga):
    resultado = db.vagas_collection.delete_one({"_id": ObjectId(id_vaga)})
    if resultado.deleted_count > 0:
        return jsonify({"mensagem": "Vaga deletada!"}), 200
    return jsonify({"erro": "Não encontrada"}), 404

@app.route('/api/candidatos', methods=['POST'])
def cadastrar_candidato():
    dados = request.json
    novo_candidato = {
        "nome": dados.get("nome"),
        "email": dados.get("email"),
        "whatsapp": dados.get("whatsapp"),
        "area_interesse": dados.get("area_interesse")
    }
    resultado = db.candidatos_collection.insert_one(novo_candidato)
    return jsonify({"mensagem": "Candidato salvo no MongoDB!", "id": str(resultado.inserted_id)}), 201

@app.route('/api/notificar/<id_vaga>', methods=['POST'])
def disparar_rpa(id_vaga):
    vaga = db.vagas_collection.find_one({"_id": ObjectId(id_vaga)})
    if not vaga:
        return jsonify({"erro": "Vaga não encontrada"}), 404

    candidato = db.candidatos_collection.find_one({"area_interesse": {"$regex": vaga['area'], "$options": "i"}})
    
    if not candidato:
        candidato = db.candidatos_collection.find_one(sort=[('_id', -1)])

    if not candidato:
        return jsonify({"erro": "Nenhum candidato cadastrado no MongoDB para receber o alerta!"}), 400

    email_destino = candidato["email"]
    whatsapp_destino = candidato["whatsapp"]

    print(f"RPA acionado. Destinatário do Banco: {candidato['nome']} ({email_destino})")

    sucesso_email = rpa.enviar_email(email_destino, vaga['titulo'], vaga['descricao'])
    sucesso_whatsapp = rpa.enviar_whatsapp(whatsapp_destino, vaga['titulo'])

    status_final = "Sucesso" if (sucesso_email and sucesso_whatsapp) else "Falha Parcial/Total"
    
    log_alerta = {
        "vaga_id": ObjectId(id_vaga),
        "candidato_id": candidato['_id'],
        "status": status_final
    }
    db.alertas_collection.insert_one(log_alerta)

    return jsonify({
        "mensagem": f"Notificação enviada para {candidato['nome']}!",
        "whatsapp": "Enviado" if sucesso_whatsapp else "Erro",
        "email": "Enviado" if sucesso_email else "Erro"
    }), 200

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    mensagem_usuario = request.json.get("mensagem", "").lower()
    
    if mensagem_usuario in ["oi", "olá", "ola", "bom dia", "boa tarde"]:
        return jsonify({"resposta": "Olá! Sou o VagaBot, integrado com Inteligência Artificial. Você pode buscar vagas no banco ou me pedir qualquer dica sobre mercado de trabalho e carreira!"}), 200

    elif "vaga" in mensagem_usuario or "buscar" in mensagem_usuario:
        areas_conhecidas = ["tecnologia", "dados", "design", "marketing", "vendas", "backend", "frontend"]
        area_detectada = next((area for area in areas_conhecidas if area in mensagem_usuario), None)

        if area_detectada:
            filtro = {"area": {"$regex": area_detectada, "$options": "i"}}
            total = db.vagas_collection.count_documents(filtro)
            resposta = f"Consultei nosso banco: Temos {total} vaga(s) de {area_detectada.capitalize()} abertas. Cadastre seu contato no painel esquerdo para receber os alertas RPA."
        else:
            total_geral = db.vagas_collection.count_documents({})
            resposta = f"Nosso banco tem {total_geral} vagas ativas. Qual área você procura? (ex: 'vagas de tecnologia')"
        
        return jsonify({"resposta": resposta}), 200

    else:
        try:
            prompt_contexto = f"Você é o VagaBot, um assistente virtual de RH de um projeto universitário. Responda de forma amigável, educada e curta (máximo de 3 frases). O usuário perguntou: '{mensagem_usuario}'"
            
            resposta_ia = ia_model.generate_content(prompt_contexto)
            
            return jsonify({"resposta": f"(Resposta via IA): {resposta_ia.text}"}), 200
            
        except Exception as e:
            print(f"ERRO REAL DA IA: {e}")
            return jsonify({"resposta": "Desculpe, minha conexão com a rede neural da IA falhou no momento. Tente novamente!"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)