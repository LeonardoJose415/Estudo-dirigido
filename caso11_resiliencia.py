import os
import socket
import time
import paramiko
from conexao import conectar, executar

os.environ.setdefault("SSH_SENHA", "Redes@2026")

INVENTARIO_TESTE = [
    {"nome": "SAUDAVEL",      "host": "127.0.0.1",    "porta": 22,   "usuario": "r1"},
    {"nome": "SENHA-ERRADA",  "host": "127.0.0.1",    "porta": 22,   "usuario": "usuario_invalido"},
    {"nome": "PORTA-FECHADA", "host": "127.0.0.1",    "porta": 2299, "usuario": "r1"},
    {"nome": "SEM-RESPOSTA",  "host": "10.255.255.1", "porta": 22,   "usuario": "r1"},
]

TENTATIVAS = 3
ESPERA_BASE = 2

def classificar(erro):
    """Devolve (categoria, causa provável, vale a pena repetir?)."""
    if isinstance(erro, paramiko.AuthenticationException):
        return "AUTENTICACAO", "usuario/senha/chave invalidos", False
    if isinstance(erro, paramiko.ssh_exception.NoValidConnectionsError):
        return "CONEXAO RECUSADA", "servico SSH parado ou porta bloqueada", False
    if isinstance(erro, (socket.timeout, TimeoutError)):
        return "TIMEOUT", "equipamento desligado, rota ausente ou firewall", True
    if isinstance(erro, socket.gaierror):
        return "NOME INVALIDO", "DNS ou endereco incorreto", False
    if isinstance(erro, paramiko.SSHException):
        return "ERRO SSH", f"falha de protocolo: {erro}", True
    return "INESPERADO", f"{type(erro).__name__}: {erro}", False

def conectar_com_retry(disp):
    ultima = None
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            return conectar(disp, timeout=4), tentativa
        except Exception as e:
            categoria, causa, repetir = classificar(e)
            ultima = (categoria, causa, tentativa)
            if not repetir:
                break
            if tentativa < TENTATIVAS:
                espera = ESPERA_BASE * 2 ** (tentativa - 1)
                print(f"  [{disp['nome']}] tentativa {tentativa} falhou ({categoria}), "
                      f"nova tentativa em {espera}s")
                time.sleep(espera)
    return None, ultima

relatorio = []
for disp in INVENTARIO_TESTE:
    cliente, info = conectar_com_retry(disp)
    if cliente:
        _, saida, _ = executar(cliente, "hostname")
        cliente.close()
        relatorio.append((disp["nome"], "OK", f"hostname={saida} (tentativa {info})"))
    else:
        categoria, causa, tentativas = info
        relatorio.append((disp["nome"], categoria, f"{causa} (tentativas: {tentativas})"))

print("\n=== RELATORIO FINAL ===")
for nome, estado, detalhe in relatorio:
    print(f"{nome:<14} {estado:<18} {detalhe}")
