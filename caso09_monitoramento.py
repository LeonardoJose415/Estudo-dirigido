from concurrent.futures import ThreadPoolExecutor
import json
from conexao import conectar, executar

LIMITE_DISCO = 80
LIMITE_CARGA = 2.0

def verificar(disp):
    resultado = {
        "nome": disp["nome"], "disco": None, "carga": None,
        "sshd": None, "alertas": [], "estado": "OK"
    }
    try:
        cliente = conectar(disp)
    except Exception as e:
        resultado["estado"] = "FALHA"
        resultado["alertas"].append(f"inacessivel ({type(e).__name__})")
        return resultado
    
    try:
        _, disco, _ = executar(cliente, "df --output=pcent / | tail -1 | tr -d ' %'")
        _, carga, _ = executar(cliente, "cut -d' ' -f1 /proc/loadavg")
        codigo, _, _ = executar(cliente, "pgrep -x sshd > /dev/null")
        
        resultado["disco"] = int(disco)
        resultado["carga"] = float(carga)
        resultado["sshd"] = "ativo" if codigo == 0 else "parado"
        
        if resultado["disco"] > LIMITE_DISCO:
            resultado["alertas"].append(f"disco em {resultado['disco']}%")
        if resultado["carga"] > LIMITE_CARGA:
            resultado["alertas"].append(f"carga alta ({resultado['carga']})")
        if resultado["sshd"] != "ativo":
            resultado["alertas"].append("servico sshd parado")
        
        if resultado["alertas"]:
            resultado["estado"] = "ALERTA"
    except Exception as e:
        resultado["estado"] = "FALHA"
        resultado["alertas"].append(f"erro na coleta ({type(e).__name__})")
    finally:
        cliente.close()
    
    return resultado

with open("inventario.json", encoding="utf-8") as f:
    inventario = json.load(f)

with ThreadPoolExecutor(max_workers=10) as pool:
    resultados = list(pool.map(verificar, inventario))

print(f"{'DISP':<5}{'ESTADO':<8}{'DISCO':<8}{'CARGA':<8}{'SSHD':<8}ALERTAS")
print("-" * 70)
for r in resultados:
    disco = f"{r['disco']}%" if r["disco"] is not None else "-"
    carga = r["carga"] if r["carga"] is not None else "-"
    print(f"{r['nome']:<5}{r['estado']:<8}{disco:<8}{str(carga):<8}"
          f"{(r['sshd'] or '-'):<8}{'; '.join(r['alertas'])}")
