import json
import re
from conexao import conectar, executar

ARQUIVO = "~/dispositivo.cfg"

def validar(chave, valor):
    padrao = r"[A-Za-z0-9_.\-]+"
    if not (re.fullmatch(padrao, chave) and re.fullmatch(padrao, valor)):
        raise ValueError(f"Valor invalido: {chave}={valor}")

def aplicar(disp, chave, valor):
    cliente = conectar(disp)
    try:
        # (a) cópia de segurança
        executar(cliente, f"cp {ARQUIVO} {ARQUIVO}.bak")
        
        # (b) alteração idempotente
        comando = (
            f"if grep -q '^{chave}=' {ARQUIVO}; then "
            f"sed -i 's/^{chave}=.*/{chave}={valor}/' {ARQUIVO}; "
            f"else echo '{chave}={valor}' >> {ARQUIVO}; fi"
        )
        codigo, _, erro = executar(cliente, comando)
        if codigo != 0:
            raise RuntimeError(f"falha ao aplicar: {erro}")
        
        # (c) verificação em duas camadas
        codigo, saida, _ = executar(cliente, f"grep -c '^{chave}=' {ARQUIVO}")
        codigo_exato, _, _ = executar(cliente, f"grep -qx '{chave}={valor}' {ARQUIVO}")
        if codigo_exato != 0 or saida != "1":
            # (d) reversão automática
            executar(cliente, f"cp {ARQUIVO}.bak {ARQUIVO}")
            return "REVERTIDO (verificacao falhou)"
        
        return "APLICADO"
    finally:
        cliente.close()

chave, valor = "ntp_server", "10.0.0.50"
validar(chave, valor)

with open("inventario.json", encoding="utf-8") as f:
    inventario = json.load(f)

for disp in inventario:
    try:
        print(f"{disp['nome']}: {aplicar(disp, chave, valor)}")
    except Exception as e:
        print(f"{disp['nome']}: FALHA ({type(e).__name__}: {e})")
