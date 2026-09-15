from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml')))


from retrieval.retriever import retrieve
from generation.generator import generate
from .auth import hash_password, verify_password, create_token, get_current_user
from .database import get_connection
app = FastAPI()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    reponse: str
    sources: list
    statut: str


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, user_id: str = Depends(get_current_user)):
    chunks = retrieve(request.question)
    result = generate(request.question, chunks)
    return QueryResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}


# Modèles auth
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Routes auth
@app.post("/auth/register")
def register(request: RegisterRequest):
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe trop court")

    conn = get_connection()
    cursor = conn.cursor()

    # Vérifie si l'email existe déjà
    cursor.execute("SELECT id FROM users WHERE email = %s", (request.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Crée le compte
    hashed = hash_password(request.password)
    cursor.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s) RETURNING id",
        (request.email, hashed)
    )
    user_id = cursor.fetchone()[0]

    # Crée le quota associé
    cursor.execute(
        "INSERT INTO quotas (user_id) VALUES (%s)",
        (str(user_id),)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Compte créé", "user_id": str(user_id)}


@app.post("/auth/login")
def login(request: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE email = %s",
        (request.email,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not verify_password(request.password, user[1]):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")

    token = create_token(str(user[0]))
    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me")
def me(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
