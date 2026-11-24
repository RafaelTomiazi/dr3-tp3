# Mala Pronta: agente de viagem com LangChain (DR3 TP3)

Trabalho do TP3 da disciplina Desenvolvimento de Data-Driven Apps com Python (Infnet).
Autor: Rafael Celestino Tomiazi.
Repositório: https://github.com/RafaelTomiazi/dr3-tp3

## O problema

Quem vai viajar acaba abrindo três ou quatro sites para decidir coisas simples: o app do tempo para saber se leva casaco, um conversor de moeda para saber quanto o real rende, e uma calculadora para dividir o dinheiro pelos dias. Cada site responde só um pedaço, e você mesmo tem que juntar tudo e lembrar o que já descobriu.

## A solução

O **Mala Pronta** é um agente que conversa em português e junta tudo isso numa conversa só:

- **Objetivo:** responder dúvidas práticas de viagem com dados reais do dia (clima e câmbio), sem inventar número.
- **Público-alvo:** brasileiros planejando uma viagem curta, principalmente para o exterior.
- **Funcionalidades:** previsão do tempo da cidade de destino, conversão de moedas pela cotação do dia, divisão do orçamento por dia, e memória da conversa (destino, dias e dinheiro informados antes).

### Como funciona

| Peça | O que é | Arquivo |
|---|---|---|
| LLM | `gemini-3.8-flash` (Google, usado nos testes) ou `gpt-4o-mini` (OpenAI), escolhido pela chave no `.env` | `agente/agente.py` |
| Ferramenta 1 | `previsao_tempo(cidade, dias)`: API Open-Meteo (geocodificação + previsão), sem chave | `agente/ferramentas.py` |
| Ferramenta 2 | `converter_moeda(valor, de, para)`: API Frankfurter (cotação do Banco Central Europeu), sem chave | `agente/ferramentas.py` |
| Ferramenta 3 | `orcamento_diario(total, dias)`: divisão simples, para o modelo não errar a conta | `agente/ferramentas.py` |
| ReAct | `create_agent` do LangChain: o modelo raciocina, chama uma ferramenta (ação), lê o resultado (observação) e repete até conseguir responder | `agente/agente.py` |
| Memória | `InMemorySaver` do LangGraph: cada conversa tem um `thread_id`, e o histórico inteiro volta para o modelo a cada pergunta | `agente/agente.py` |
| Interface | Chat em Streamlit, que mostra o raciocínio (ações e observações) embaixo de cada resposta; também há uma versão de linha de comando | `app.py`, `cli.py` |

Cada ferramenta tem nome, descrição (a docstring, que é o que o LLM lê para decidir quando usar) e tratamento de erro. Cidade inexistente, API fora do ar ou moeda inválida voltam como texto explicando o problema, e o agente repassa isso ao usuário em vez de quebrar.

## Casos de uso testados

| # | Caso | O que valida |
|---|---|---|
| 1 | "Vou para Lisboa daqui a 2 dias e fico 3 dias. Preciso levar casaco ou guarda-chuva?" | Uso da ferramenta de clima |
| 2 | "Tenho 3000 reais para a viagem. Quanto isso dá em euro hoje?" | Uso da ferramenta de câmbio |
| 3 | "E se eu ficar 5 dias em vez de 3, quanto posso gastar por dia em euro?" | Memória: tem que lembrar o valor em euro da pergunta anterior e só então usar a ferramenta de orçamento |
| 4 | "Para onde eu disse que vou e com quanto dinheiro?" | Memória pura, sem ferramenta |
| 5 | "Qual a previsão do tempo em Cidadeinexistenteabc?" | Tratamento de erro |

Os casos rodam com `python casos_de_uso.py`. As respostas completas e as ferramentas que o agente escolheu ficam em [`resultados_casos_de_uso.md`](resultados_casos_de_uso.md). Resultado da rodada de 23/11/2026 com o `gemini-3.8-flash`:

| # | Ferramentas que o agente escolheu | Resultado observado |
|---|---|---|
| 1 | `previsao_tempo` | Leu a previsão de Lisboa (10 a 18 °C, chuva de 5% a 20% no período) e respondeu: leve casaco, guarda-chuva provavelmente não |
| 2 | `converter_moeda` | R$ 3.000,00 = 457,23 € (1 BRL = 0,1524 EUR, cotação do dia) |
| 3 | `orcamento_diario` | Lembrou os 457,23 € da pergunta anterior, sem converter de novo, e dividiu: 91,45 € por dia |
| 4 | nenhuma | Respondeu "Lisboa, R$ 3.000,00 (cerca de 457,23 €)" só com a memória |
| 5 | `previsao_tempo` | A ferramenta não achou a cidade e o agente pediu para conferir o nome, sem quebrar |

No caso 3 o agente pulou a conversão porque o valor em euro já estava no histórico. É a memória economizando uma chamada de ferramenta.

## Como executar

```bash
python -m venv venv
venv\Scripts\activate            # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # e cole a sua GOOGLE_API_KEY (ou OPENAI_API_KEY)

streamlit run app.py             # interface web
python cli.py                    # ou no terminal
python casos_de_uso.py           # roda os casos de uso e salva os resultados
```

## Reflexão: o que o agente facilita

Sem o agente, a pessoa abre o site do tempo, procura a cidade, lê a previsão dia a dia, abre um conversor, digita o valor, copia o resultado para a calculadora e divide pelos dias. Se mudar um dado ("e se eu ficar 5 dias?"), refaz tudo. Com o agente é uma frase. Ele decide sozinho quais ferramentas usar e em que ordem, e a memória evita repetir o destino e o valor a cada pergunta.

O ganho em relação a um chatbot comum é que os números vêm das APIs no momento da pergunta, não da memória de treino do modelo. Um LLM sozinho chutaria a cotação e a temperatura. Aqui ele só redige a resposta em cima do que as ferramentas devolveram, e o raciocínio fica visível na tela para conferir.

Limites: a memória fica em RAM e some quando o app reinicia; a cotação é a de referência do BCE (casas de câmbio cobram mais); a previsão vai só até 7 dias.

## Uso de IA

O enunciado tem sinal verde para IA, com citação. Usei o Claude (Anthropic) como apoio para estruturar o código e revisar este README. O LLM usado dentro da aplicação é o indicado na tabela acima.
