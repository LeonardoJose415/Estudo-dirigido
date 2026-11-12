def main():
    # Carregar inventário
    with open("inventario.json", "r", encoding="utf-8") as f:
        inventario = json.load(f)

    dispositivos = inventario.get("roteadores", [])
    relatorio_final = []

    print(f"=== Iniciando Coleta Concorrente em {len(dispositivos)} dispositivos ===")

    # Executa as conexões em paralelo usando até 5 threads
    max_workers = min(5, len(dispositivos)) if dispositivos else 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(processar_dispositivo, disp)
            for disp in dispositivos
        ]

        for future in as_completed(futures):
            relatorio_final.append(future.result())

    # Salvar relatório final
    with open("relatorio_final.json", "w", encoding="utf-8") as f:
        json.dump(relatorio_final, f, indent=4, ensure_ascii=False)

    print("\n[✓] Relatório final gerado com sucesso em 'relatorio_final.json'!")