from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, EmailStr
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml')))


from retrieval.retriever import retrieve
from generation.generator import generate
from ingestion.pdf_loader import load_pdf
from ingestion.cleaner import clean_pages
from ingestion.chunker import split_pages
from embedding.embedder import embed_and_store
from .auth import hash_password, verify_password, create_token, get_current_user
from .database import get_connection
from .storage import upload_file, download_file

app = FastAPI()

# Plan free → max 1 doc
# Plan pro  → max 50 docs
PLAN_LIMITS = {
    "free": 1,
    "pro": 50
}


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    reponse: str
    sources: list
    statut: str


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, user_id: str = Depends(get_current_user)):
    chunks = retrieve(request.question, user_id=user_id)
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


# Upload de documents
@app.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    if file.content_type != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT u.plan, q.docs_uploaded FROM users u JOIN quotas q ON q.user_id = u.id WHERE u.id = %s",
        (user_id,)
    )
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Utilisateur ou quota introuvable")

    plan, docs_uploaded = row
    limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

    if docs_uploaded >= limit:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Quota de documents atteint pour votre plan")

    file_bytes = await file.read()
    storage_key = upload_file(file_bytes, file.filename, user_id)

    cursor.execute(
        "INSERT INTO documents (user_id, filename, storage_url, status) VALUES (%s, %s, %s, 'processing') RETURNING id",
        (user_id, file.filename, storage_key)
    )
    document_id = cursor.fetchone()[0]

    cursor.execute(
        "UPDATE quotas SET docs_uploaded = docs_uploaded + 1 WHERE user_id = %s",
        (user_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    background_tasks.add_task(process_document, str(document_id), storage_key, user_id)

    return {"message": "Document reçu, ingestion en cours", "document_id": str(document_id)}


def process_document(document_id: str, storage_key: str, user_id: str):
    status = "failed"

    try:
        file_bytes = download_file(storage_key)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            pages = load_pdf(tmp_path)
        finally:
            os.remove(tmp_path)

        pages = clean_pages(pages)
        chunks = split_pages(pages)
        embed_and_store(chunks, user_id=user_id)

        status = "ready"
    except Exception:
        status = "failed"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE documents SET status = %s WHERE id = %s",
        (status, document_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
