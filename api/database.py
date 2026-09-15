import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))