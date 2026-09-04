from config import ADMIN_MATRICULAS

print("Matrículas administrativas configuradas:")
for indice, matricula in enumerate(ADMIN_MATRICULAS, start=1):
    print(f"Admin {indice}: {matricula or '[slot vazio]'}")
