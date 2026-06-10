from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["vagabot_db"]

vagas_collection = db["vagas"]
candidatos_collection = db["candidatos"]
alertas_collection = db["alertas"]

if __name__ == "__main__":
    print("Conectado ao MongoDB! Coleções no banco de dados:", db.list_collection_names())