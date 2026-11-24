# Roda os casos de uso definidos no README e salva o que aconteceu em
# resultados_casos_de_uso.md (pergunta, ferramentas usadas e resposta).
# Os casos 1 a 4 sao a mesma conversa, pra testar a memoria.
from datetime import datetime

from agente.agente import criar_agente, perguntar

CASOS = [
    ("1. Clima (tool previsao_tempo)", "conversa-1", "Vou para Lisboa daqui a 2 dias e fico 3 dias. Preciso levar casaco ou guarda-chuva?"),
    ("2. Câmbio (tool converter_moeda)", "conversa-1", "Tenho 3000 reais para a viagem. Quanto isso dá em euro hoje?"),
    ("3. Memória + duas tools", "conversa-1", "E se eu ficar 5 dias em vez de 3, quanto posso gastar por dia em euro?"),
    ("4. Memória pura", "conversa-1", "Para onde eu disse que vou e com quanto dinheiro?"),
    ("5. Erro tratado", "conversa-2", "Qual a previsão do tempo em Cidadeinexistenteabc?"),
]


def main():
    agente = criar_agente()
    linhas = [f"# Resultados dos casos de uso\n\nRodado em {datetime.now():%d/%m/%Y %H:%M}.\n"]
    for titulo, conversa, pergunta in CASOS:
        resposta, passos = perguntar(agente, pergunta, conversa)
        usadas = [p["ferramenta"] for p in passos if p["tipo"] == "ação"]
        print(titulo, "->", usadas)
        linhas.append(f"## {titulo}\n\n**Pergunta:** {pergunta}\n\n**Ferramentas usadas:** {', '.join(usadas) or 'nenhuma'}\n")
        for p in passos:
            if p["tipo"] == "observação":
                linhas.append(f"> Observação ({p['ferramenta']}): {p['resultado']}\n".replace("\n-", "\n> -"))
        linhas.append(f"**Resposta:** {resposta}\n")
    with open("resultados_casos_de_uso.md", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print("Salvo em resultados_casos_de_uso.md")


if __name__ == "__main__":
    main()
