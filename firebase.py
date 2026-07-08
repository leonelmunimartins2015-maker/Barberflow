import firebase_admin
from firebase_admin import credentials, firestore
import os
import json


def iniciar_firebase():

    try:

        chave = os.environ.get("FIREBASE_KEY")

        cred = credentials.Certificate(
            json.loads(chave)
        )

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        return db

    except Exception as erro:

        print("Erro Firebase:", erro)

        return None
