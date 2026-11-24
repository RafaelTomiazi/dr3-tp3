# Interface de linha de comando. Rodar: python cli.py  (sair: digite "sair")
from agente.agente import SemChaveDeAPI, criar_agente, perguntar


def main():
    try:
        agente = criar_agente()
    except SemChaveDeAPI as erro:
        print(erro)
        return
    print("Mala Pronta - agente de viagem. Digite 'sair' para terminar.\n")
    while True:
        pergunta = input("Você: ").strip()
        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        if not pergunta:
            continue
        try:
            resposta, passos = perguntar(agente, pergunta, "cli")
        except Exception as erro:
            print("Erro ao falar com o modelo:", erro)
            continue
        for p in passos:
            if p["tipo"] == "ação":
                print(f"  [ação] {p['ferramenta']}({p['argumentos']})")
            else:
                print(f"  [observação] {p['resultado'][:200]}")
        print("Agente:", resposta, "\n")


if __name__ == "__main__":
    main()
