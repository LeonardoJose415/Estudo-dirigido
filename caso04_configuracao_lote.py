import json
from conexao import conectar, executar


def aplicar_configuracao_com_rollback(dispositivo: dict) -> bool:
    """Aplica a configuração no dispositivo. Se falhar, restaura o backup."""
    nome = dispositivo.get("nome", "Desconhecido")
    host = dispositivo.get("host")
    usuario = dispositivo.get("usuario")

    arquivo_alvo = f"/tmp/resolv_test_{usuario}.conf"
    arquivo_backup = f"/tmp/resolv_test_{usuario}.conf.bak"

    print(f"\n[*] Processando {nome} ({host})...")

    try:
        # 1. Estabelece a conexão usando a função do conexao.py
        cliente = conectar(dispositivo)

        # 2. Criar backup se o arquivo original já existir
        cmd_backup = f"cp {arquivo_alvo} {arquivo_backup} 2>/dev/null || true"
        executar(cliente, cmd_backup)
        print(f"  [+] Backup gerado em '{arquivo_backup}' (se existia).")

        # 3. Escrever a nova configuração
        nova_config = "nameserver 8.8.8.8\\nnameserver 1.1.1.1\\n"
        cmd_aplicar = f"echo '{nova_config}' > {arquivo_alvo}"
        codigo, stdout, stderr = executar(cliente, cmd_aplicar)

        # 4. Verificar código de retorno para acionar Rollback se necessário
        if codigo != 0:
            print(f"  [!] Falha ao aplicar configuração (código {codigo}). Iniciando Rollback...")
            cmd_rollback = f"mv {arquivo_backup} {arquivo_alvo} 2>/dev/null || rm -f {arquivo_alvo}"
            executar(cliente, cmd_rollback)
            print("  [✗] Rollback concluído. Estado original restaurado.")
            cliente.close()
            return False

        print(f"  [✓] Configuração aplicada com sucesso em {arquivo_alvo}.")
        executar(cliente, f"rm -f {arquivo_backup}")
        cliente.close()
        return True

    except Exception as e:
        print(f"  [✗] Erro de conexão/execução em {nome}: {e}")
        return False


def main():
    with open("inventario.json", "r", encoding="utf-8") as f:
        inventario = json.load(f)

    sucessos = 0
    print("=== Iniciando Configuração em Lote com Mecanismo de Rollback ===")

    for dispositivo in inventario:
        if aplicar_configuracao_com_rollback(dispositivo):
            sucessos += 1

    print(f"\n[Summary] Concluído: {sucessos}/{len(inventario)} dispositivos processados.")


if __name__ == "__main__":
    main()