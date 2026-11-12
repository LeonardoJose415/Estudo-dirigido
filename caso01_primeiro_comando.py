from conexao import conectar, executar

dispositivo = {"nome": "R1", "host": "127.0.0.1", "porta": 22, "usuario": "r1"}
comandos = ["whoami", "hostname", "uptime -p", "comando-inexistente"]

cliente = conectar(dispositivo)
try:
    for cmd in comandos:
        codigo, saida, erro = executar(cliente, cmd)
        print(f"$ {cmd}")
        print(f"  codigo: {codigo}")
        print(f"  saida : {saida or '(vazia)'}")
        print(f"  erro  : {erro or '(vazio)'}\n")
finally:
    cliente.close()
