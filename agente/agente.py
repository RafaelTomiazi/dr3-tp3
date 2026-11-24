# Monta o agente ReAct: LLM + ferramentas + memoria.
#
# O create_agent do LangChain roda o ciclo ReAct: o modelo raciocina, decide
# chamar uma ferramenta (acao), recebe o resultado (observacao) e repete ate
# ter informacao pra responder. A memoria e o InMemorySaver do LangGraph:
# cada conversa tem um thread_id e o historico inteiro volta pro modelo a cada
# pergunta, entao ele lembra destino, orcamento etc.

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from agente.ferramentas import FERRAMENTAS

load_dotenv()

INSTRUCOES = """Você é o Mala Pronta, um assistente de planejamento de viagens para brasileiros.
Responda sempre em português, de forma curta e prática.

Como trabalhar (ReAct):
1. Pense no que o usuário precisa e quais dados faltam.
2. Se faltar dado de clima, câmbio ou divisão de orçamento, use a ferramenta certa. Não invente números.
3. Leia o resultado da ferramenta e decida se precisa de outra.
4. Só então responda, citando os números que vieram das ferramentas.

Use o histórico da conversa: se o usuário já disse destino, datas ou orçamento, não pergunte de novo.
Se uma ferramenta der erro, explique o problema e sugira o que o usuário pode fazer."""


class SemChaveDeAPI(Exception):
    pass


def criar_llm():
    # escolhe o provedor pela chave que estiver no .env (Gemini primeiro, porque tem plano gratis)
    if os.getenv("GOOGLE_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=os.getenv("MODELO", "gemini-3.8-flash"), temperature=0)
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI

        # gpt-4o-mini: barato, rapido e bom em chamar ferramentas
        return ChatOpenAI(model=os.getenv("MODELO", "gpt-4o-mini"), temperature=0, timeout=60, max_retries=2)
    raise SemChaveDeAPI("Coloque GOOGLE_API_KEY ou OPENAI_API_KEY no arquivo .env (veja o .env.example).")


def criar_agente():
    return create_agent(
        model=criar_llm(),
        tools=FERRAMENTAS,
        system_prompt=INSTRUCOES,
        checkpointer=InMemorySaver(),  # memoria conversacional
    )


def perguntar(agente, pergunta, conversa_id="padrao"):
    """Manda a pergunta e devolve (resposta_final, passos), onde passos e a
    lista do raciocinio: cada acao (ferramenta + argumentos) e a observacao."""
    config = {"configurable": {"thread_id": conversa_id}}
    antes = len(agente.get_state(config).values.get("messages", [])) if agente.get_state(config).values else 0
    resultado = agente.invoke({"messages": [HumanMessage(pergunta)]}, config)
    novas = resultado["messages"][antes:]

    passos = []
    for msg in novas:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for chamada in msg.tool_calls:
                passos.append({"tipo": "ação", "ferramenta": chamada["name"], "argumentos": chamada["args"]})
        elif isinstance(msg, ToolMessage):
            passos.append({"tipo": "observação", "ferramenta": msg.name, "resultado": msg.content})
    return texto_da_resposta(resultado["messages"][-1]), passos


def texto_da_resposta(mensagem):
    # o Gemini devolve a resposta como lista de blocos ({'type': 'text', ...});
    # a OpenAI devolve string. junto so os blocos de texto
    conteudo = mensagem.content
    if isinstance(conteudo, str):
        return conteudo
    return "".join(b.get("text", "") for b in conteudo if isinstance(b, dict) and b.get("type") == "text")
