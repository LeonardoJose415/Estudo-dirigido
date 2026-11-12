import json
import os
from datetime import datetime
from conexao import conectar, executar

def carregar_inventario(caminho="inventario.json"):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    dispositivos = carregar_inventario()
    comandos = ["hostname", "whoami", "uptime -p"]
    relatorio_geral = []
    
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=== INICIANDO COLETA COM GERAÇÃO DE RELATÓRIOS ===\n")

    for dev in dispositivos:
        nome = dev["nome"]
        dados_dispositivo = {
            "dispositivo": nome,
            "host": dev["host"],
            "usuario": dev["usuario"],
            "timestamp": timestamp,
            "status": "SUCESSO",
            "comandos": {}
        }
        
        caminho_log = f"logs/{nome.lower()}_coleta.log"
        print(f"--- Conectando a {nome} ---")
        
        try:
            cliente = conectar(dev)
            with open(caminho_log, "w", encoding="utf-8") as log_file:
                log_file.write(f"=== LOG DE COLETA: {nome} ({timestamp}) ===\n\n")
                
                for cmd in comandos:
                    codigo, saida, erro = executar(cliente, cmd)
                    
                    dados_dispositivo["comandos"][cmd] = {
                        "codigo_retorno": codigo,
                        "saida": saida,
                        "erro": erro
                    }
                    
                    log_file.write(f"$ {cmd}\n")
                    log_file.write(f"Código: {codigo}\n")
                    log_file.write(f"Saída : {saida}\n")
                    if erro:
                        log_file.write(f"Erro  : {erro}\n")
                    log_file.write("-" * 40 + "\n")
                    
            cliente.close()
            print(f"  [OK] Dados coletados e salvos em '{caminho_log}'")
            
        except Exception as e:
            dados_dispositivo["status"] = "FALHA"
            dados_dispositivo["erro_conexao"] = str(e)
            print(f"  [ERRO] Falha ao conectar em {nome}: {e}")

        relatorio_geral.append(dados_dispositivo)
        print()

    # Salva o relatório consolidado em JSON
    caminho_json = "relatorio_final.json"
    with open(caminho_json, "w", encoding="utf-8") as json_file:
        json.dump(relatorio_geral, json_file, indent=2, ensure_ascii=False)

    print(f"=== PROCESSO CONCLUÍDO ===")
    print(f"Relatório consolidado salvo em: {caminho_json}")

if __name__ == "__main__":
    main()
