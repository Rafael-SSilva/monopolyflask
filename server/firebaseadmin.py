import firebase_admin
from uuid import uuid4
from firebase_admin import credentials, firestore



def connection():
  cred = credentials.Certificate("C:/projects/monopoly/server/firebase_sdk.json")

  firebase_admin.initialize_app(cred)

  db = firestore.client()

  return db 

# doc_ref = db.collection('salas').document(str(uuid4()))

# doc_ref.set({
#   'nome': 'primeira sala do jogo'
# })

def get_alll(**Kwargs):
  #consulta geral em uma collection.
  db = connection()
  rooms_ref = db.collection('salas')
  rooms = rooms_ref.stream()

  return rooms.to_dict()



