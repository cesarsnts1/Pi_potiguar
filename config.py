import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_SENHA = os.getenv("ADMIN_SENHA", "poti345")
ADMIN_MATRICULAS = [
    os.getenv("ADMIN_MATRICULA_1", "20231101110023"),
    os.getenv("ADMIN_MATRICULA_2", "20231101110049"),
    os.getenv("ADMIN_MATRICULA_3", "20231101110015"),
    os.getenv("ADMIN_MATRICULA_4", "20221101110009"),
]
