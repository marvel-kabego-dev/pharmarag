from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml')))

from ml.retrieval.retriever import retrieve
from ml.generation.generator import generate

app = FastAPI()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    reponse: str
    sources: list
    statut: str


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    chunks = retrieve(request.question)
    result = generate(request.question, chunks)
    return QueryResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}
