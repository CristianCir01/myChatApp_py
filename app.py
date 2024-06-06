from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId, json_util
import json
import smtplib
from flask_mail import Mail, Message
from flask_cors import CORS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random



app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # Consenti a tutte le origini di accedere a tutte le risorse
# Configurazione del database MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['chat_app_db']  # Nome del database
chats_collection = db['chats']  # Collezione per le chat
users_collection = db['users']  # Collezione per gli utenti
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'chatmesupp00@gmail.com'
app.config['MAIL_PASSWORD'] = 'jlmr xkqz bakj gbfj'
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)
'''
# Mock data per gli utenti
mockUsers = [
    { "id": 1, "username": "user1", "password": "password1","email":"exemple@gmail.com" },
    { "id": 2, "username": "user2", "password": "password2" ,"email":"exemple@gmail.com" },
    { "id": 3, "username": "user3", "password": "password3","email":"exemple@gmail.com"  },
    { "id": 4, "username": "user4", "password": "password4","email":"exemple@gmail.com"  },
    { "id": 5, "username": "user5", "password": "password5" ,"email":"exemple@gmail.com" }
]

# Mock data per le chat
mockChats = [
    { "chatid": 1, "userId1": 1, "userId2": 2, "list": [ 
        { "sender": 1, "message": "Hello from user1" },
        { "sender": 2, "message": "Hi there from user2" }
    ]},
    { "chatid": 2, "userId1": 1, "userId2": 3, "list": [ 
        { "sender": 1, "message": "Hello from user1" },
        { "sender": 3, "message": "Hi there from user2" }
    ]},
    { "chatid": 3, "userId1": 1, "userId2": 4, "list": [ 
        { "sender": 1, "message": "Hello from user1" },
        { "sender": 4, "message": "Hi there from user2" }
    ]},
    { "chatid": 4, "userId1": 1, "userId2": 5, "list": [ 
        { "sender": 1, "message": "Hello from user1" },
        { "sender": 5, "message": "Hi there from user2" }
    ]}
]'''
#Aggiungere un user
@app.route('/register', methods=['POST'])
def register_user():
    user_data = request.json
    username = user_data.get("username")
    password = user_data.get("password")
    email = user_data.get("email")
    id_random=random.randint(1,10000)
    # Verifica se l'utente esiste già
    existing_user = users_collection.find_one({"email": email})
    
    
    existing_id=users_collection.find_one({"id":id_random})
    if existing_id:
        while existing_id==True:
            id_random=random.randint(1,10000)
    if existing_user:
        return jsonify({"error": "L'utente esiste già"}), 400
    
    # Crea un nuovo utente
    new_user = {
        "id":id_random,
        "username": username,
        "password": password,
        "email": email
    }
    
    # Salva il nuovo utente nel database
    result = users_collection.insert_one(new_user)
    
    if result.inserted_id:
        return jsonify({"message": "Utente registrato con successo"})
    else:
        return jsonify({"error": "Errore durante la registrazione dell'utente"}), 500
def check_email(recipient_email):
    """
    Controlla se l'email esiste nella collezione utenti.
    """
    return users_collection.find_one({"email": recipient_email})

@app.route('/recover_password', methods=['POST'])
def recover_password():
    """
    Endpoint per recuperare la password dell'utente.
    """

    data = request.get_json()
    email = data.get('email')

   
    if not email:
        return jsonify({"error": "Email mancante"}), 400

    user = check_email(email)
    if user:
        password = user['password']
        msg = Message(
        subject='recover_password', 
        sender='chatmesupp00@gmail.com',  # Ensure this matches MAIL_USERNAME
        recipients=[email]  # Replace with actual recipient's email
    )
        msg.body = f"In seguito vi forniamo la password come richiesto: {password}"
    
        try:
            mail.send(msg)
            return jsonify({"message": "Email inviata con successo"}), 200
        except Exception as e:
            print(f"Errore nell'invio dell'email: {e}")
            return jsonify({"error": "Errore nell'invio dell'email"}), 500
    else:
        return jsonify({"message": "Email non trovata"}), 404

# EndPoint dell'applicazione
@app.route('/users/<int:user_id>/chats', methods=['GET'])
def get_user_chats(user_id):
    user_chats = list(chats_collection.find({"$or": [{"userId1": user_id}, {"userId2": user_id}]}))
    for chat in user_chats:
        chat['_id'] = str(chat['_id'])  # Converti ObjectId in stringa
    return jsonify(user_chats)
# Retrive chat tra due utenti
@app.route('/chats/<int:user_id1>/<int:user_id2>', methods=['GET'])
def get_chat_between_users(user_id1, user_id2):
    chat = chats_collection.find_one({"$or": [{"userId1": user_id1, "userId2": user_id2}, {"userId1": user_id2, "userId2": user_id1}]})
    if chat:
        chat['_id'] = str(chat['_id'])  # Converti ObjectId in stringa
        return jsonify(chat)
    else:
        return jsonify({"error": "Chat non trovata"}), 404
# Retrive user data
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users_collection.find_one({"id": user_id})
    if user:
        user['_id'] = str(user['_id'])  # Converti ObjectId in stringa
        return jsonify(user)
    else:
        return jsonify({"error": "Utente non trovato"}), 404
 # LOGIN
@app.route('/login', methods=['POST'])
def login_user():
    login_data = request.json
    email = login_data.get("email")
    password = login_data.get("password")

    user = users_collection.find_one({"email": email, "password": password})

    if user:
        user['_id'] = str(user['_id'])
        return json_util.dumps(user)
    else:
        return jsonify({"error": "Credenziali non valide"}), 401

 # Invio di un messaggio tra due utenti
@app.route('/send_message/<int:user_id1>/<int:user_id2>', methods=['POST'])
def send_message(user_id1,user_id2):
    message_data = request.json
    sender = message_data.get("sender")
    message = message_data.get("message")
    
    # Esegui la logica per inviare il messaggio tra gli utenti
    # Ad esempio, puoi salvare il messaggio nella chat appropriata nel database
    
    # Esempio di logica per salvare il messaggio nella chat
    # In questo caso, si suppone che ci sia una chat tra gli utenti con user_id1 e user_id2
    # Puoi personalizzare questa logica in base alla tua implementazione effettiva
    chat = chats_collection.find_one({"$or": [{"userId1": user_id1, "userId2": user_id2}, {"userId1": user_id2, "userId2": user_id1}]})
    
    if chat:
        new_message = {
            "sender": sender,
            "message": message
        }
        
        chats_collection.update_one(
            {"_id": chat['_id']},
            {"$push": {"list": new_message}}
        )
        
        return jsonify({"message": "Messaggio inviato con successo"})
    else:
        return jsonify({"error": "Chat non trovata"}), 404

'''# Funzione per inizializzare i dati mock nel database
def initialize_db():
    users_collection.insert_many(mockUsers)
    chats_collection.insert_many(mockChats)
'''
if __name__ == '__main__':
    #initialize_db()  # Inizializza i dati mock
    app.run(debug=True)
