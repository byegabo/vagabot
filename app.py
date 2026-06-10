from flask import Flask, request, jsonify
from flask_cors import CORS
from bson.objectid import ObjectId
import database as db 
import rpa  

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "ta rodando eba"

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

@app.route('/api/vagas/<id_vaga>', methods=['DELETE'])
def deletar_vaga(id_vaga):
    resultado = db.vagas_collection.delete_one({"_id": ObjectId(id_vaga)})
    if resultado.deleted_count > 0:
        return jsonify({"mensagem": "Vaga deletada!"}), 200
    return jsonify({"erro": "Não encontrada"}), 404

@app.route('/api/notificar/<id_vaga>', methods=['POST'])
def disparar_rpa(id_vaga):
    vaga = db.vagas_collection.find_one({"_id": ObjectId(id_vaga)})
    if not vaga:
        return jsonify({"erro": "Vaga não encontrada"}), 404

    # DADOS DE TESTE PRA APRESENTA
    # AQUI TEM QUE MUDAAAAAA
    EMAIL_TESTE = ""
    WHATSAPP_TESTE = ""  

    print(f"Iniciando automação para a vaga: {vaga['titulo']}")

    sucesso_email = rpa.enviar_email(EMAIL_TESTE, vaga['titulo'], vaga['descricao'])
    sucesso_whatsapp = rpa.enviar_whatsapp(WHATSAPP_TESTE, vaga['titulo'])

    status_final = "Sucesso" if (sucesso_email and sucesso_whatsapp) else "Falha Parcial/Total"
    log_alerta = {
        "vaga_id": ObjectId(id_vaga),
        "titulo_vaga": vaga['titulo'],
        "destinatario_email": EMAIL_TESTE,
        "destinatario_whats": WHATSAPP_TESTE,
        "status": status_final
    }
    db.alertas_collection.insert_one(log_alerta)

    return jsonify({
        "mensagem": "Processo RPA concluído!",
        "whatsapp": "Enviado" if sucesso_whatsapp else "Erro",
        "email": "Enviado" if sucesso_email else "Erro",
        "log_salvo_no_banco": status_final
    }), 200


@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    mensagem_usuario = request.json.get("mensagem", "").lower()

    if "oi" in mensagem_usuario or "olá" in mensagem_usuario or "bom dia" in mensagem_usuario:
        resposta = "Olá! Eu sou o VagaBot. Como posso te ajudar hoje? Você pode me pedir coisas como 'buscar vagas de tecnologia' ou saber sobre processos seletivos."
    elif "tecnologia" in mensagem_usuario or "ti" in mensagem_usuario or "programador" in mensagem_usuario:
        resposta = "Perfeito! Identifiquei seu interesse em Tecnologia. Você pode ver todas as vagas dessa área usando o filtro de busca no nosso painel principal!"
    elif "processo" in mensagem_usuario or "ajuda" in mensagem_usuario:
        resposta = "Dica do VagaBot: Para mandar bem nos processos seletivos, mantenha seu GitHub atualizado e revise os conceitos básicos de Python e Banco de Dados!"
    else:
        resposta = "Entendi! Não tenho certeza se posso ajudar com isso agora, mas tente pesquisar por 'vagas' ou dizer 'oi' para reiniciarmos."

    return jsonify({"resposta": resposta}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)