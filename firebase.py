# Conexão com Firebase - BarberFlow

import firebase_admin
from firebase_admin import credentials, firestore


def iniciar_firebase():

    try:
        cred = credentials.Certificate(
            "firebase_key.json"
        )

        firebase_admin.initialize_app(cred)

        db = firestore.client()

        return db

    except Exception as erro:

        print("Erro Firebase:", erro)

        return None
