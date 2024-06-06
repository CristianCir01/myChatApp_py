'''
5. **Inserire i dati mock in MongoDB**:
Puoi usare uno script Python per popolare il database con i dati mock:
python'''
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.mydatabase

mock_user = {
    'id': 1,
    'username': 'user1',
    'password': 'password1'
}

mock_chats = [
    {
        'chatid': 1,
        'userId1': 1,
        'userId2': 2,
        'list': [
            {'sender': 1, 'message': 'Hello from user1'},
            {'sender': 2, 'message': 'Hi there from user2'}
        ]
    }
]

mock_messages = [
    {'sender': 1, 'message': 'Hello from user1'},
    {'sender': 2, 'message': 'Hi there from user2'}
]