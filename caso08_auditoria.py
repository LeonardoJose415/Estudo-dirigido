import difflib
import json
from conexao import conectar

IGNORAR = ("hostname=",)

def normalizar(linhas):
    return [l.strip() for l in linhas if l.strip() and not l.startswith(IGNORAR)]

def ler_remoto(disp):
    cliente = conectar(disp)
    try:
        sftp = cliente.open_sftp()
        try:
            with sftp.open("dispositivo.cfg") as arquivo:
                return arquivo.read().decode().splitlines()
        finally:
            sftp.close()
    finally:
        cliente.close()

with open("referencia.cfg", encoding="utf-8") as f:
    referencia = normalizar(f.read().splitlines())

with open("inventario.json", encoding="utf-8") as f:
    inventario = json.load(f)

nao_conformes = 0
for disp in inventario:
    try:
        atual = normalizar(ler_remoto(disp))
        diff = list(difflib.unified_diff(
            sorted(referencia), sorted(atual),
            fromfile="referencia", tofile=disp["nome"], lineterm="",
        ))
        if diff:
            nao_conformes += 1
            print(f"[{disp['nome']}] NAO CONFORME")
            print("\n".join("  " + l for l in diff))
        else:
            print(f"[{disp['nome']}] CONFORME")
    except Exception as e:
        print(f"[{disp['nome']}] FALHA ({type(e).__name__}: {e})")

print(f"\nResumo: {nao_conformes} de {len(inventario)} equipamento(s) fora de conformidade.")
