import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "Balu",
  "mail": "s1131254@pu.edu.tw",
  "lab": 777
}

doc_ref = db.collection("靜宜資管").document("Balu")
doc_ref.set(doc)
	