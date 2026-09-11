import os
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("MYSQL_HOST", "localhost")
PORT = int(os.getenv("MYSQL_PORT", "3306"))
USER = os.getenv("MYSQL_USER", "root")
PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DATABASE = os.getenv("MYSQL_DATABASE", "pi_potiguar")

AUTO_CREATE_DATABASE = os.getenv("AUTO_CREATE_DATABASE", "true").strip().lower() in {"1", "true", "yes", "sim"}

MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA", "").strip()
MYSQL_SSL_VERIFY_CERT = os.getenv("MYSQL_SSL_VERIFY_CERT", "true").strip().lower() in {"1", "true", "yes", "sim"}


ADMIN_SENHA = os.getenv("ADMIN_SENHA", "poti345")

ADMIN_MATRICULAS = [
    os.getenv("ADMIN_MATRICULA_1", "20231101110023"),
    os.getenv("ADMIN_MATRICULA_2", "20231101110049"),
    os.getenv("ADMIN_MATRICULA_3", "20231101110015"),
    os.getenv("ADMIN_MATRICULA_4", ""),
]
