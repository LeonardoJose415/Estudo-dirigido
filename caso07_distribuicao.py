import hashlib
import json
from conexao import conectar, executar

LOCAL = "coleta.sh"
REMOTO = "coleta.sh"

def sha256_local(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(8192), b""):
            h.update(bloco)
    return h.hexdigest()

def distribuir(disp, hash_local):
    cliente = conectar(disp)
    try:
        sftp = cliente.open_sftp()
        try:
            sftp.put(LOCAL, REMOTO)
            sftp.chmod(REMOTO, 0o755)
        finally:
            sftp.close()
        
        codigo, saida, _ = executar(cliente, f"sha256sum {REMOTO}")
        if codigo != 0:
            return "FALHA: nao foi possivel calcular o hash remoto"
        
        hash_remoto = saida.split()[0]
        if hash_remoto != hash_local:
            return "ABORTADO: hash diferente, arquivo corrompido"
        
        _, resultado, _ = executar(cliente, f"./{REMOTO}")
        return "INTEGRO E EXECUTADO\n" + resultado
    finally:
        cliente.close()

hash_local = sha256_local(LOCAL)
print(f"Hash local: {hash_local}\n")

with open("inventario.json", encoding="utf-8") as f:
    inventario = json.load(f)

for disp in inventario:
    try:
        print(f"[{disp['nome']}] {distribuir(disp, hash_local)}\n")
    except Exception as e:
        print(f"[{disp['nome']}] FALHA ({type(e).__name__}: {e})\n")
