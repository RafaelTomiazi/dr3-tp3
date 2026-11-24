# Interface em Streamlit: chat com o agente e, embaixo de cada resposta, o
# raciocinio (acoes e observacoes) pra ver o ReAct funcionando.
# Rodar: streamlit run app.py

import uuid

import streamlit as st

from agente.agente import SemChaveDeAPI, criar_agente, perguntar

st.set_page_config(page_title="Mala Pronta", page_icon="🧳")
st.title("🧳 Mala Pronta")
st.caption("Agente de viagem com LangChain: clima, câmbio e orçamento por dia. Ele lembra do que você já falou.")


@st.cache_resource
def carregar_agente():
    return criar_agente()


try:
    agente = carregar_agente()
except SemChaveDeAPI as erro:
    st.error(str(erro))
    st.stop()

# cada aba do navegador tem a sua conversa (thread_id) e o seu historico
if "conversa_id" not in st.session_state:
    st.session_state.conversa_id = str(uuid.uuid4())
    st.session_state.historico = []

with st.sidebar:
    st.subheader("Experimente")
    st.markdown(
        "- Vou para Lisboa semana que vem. Preciso de casaco?\n"
        "- Tenho 3000 reais, quanto dá em euro?\n"
        "- E se eu ficar 5 dias, quanto posso gastar por dia?"
    )
    if st.button("Nova conversa"):
        st.session_state.conversa_id = str(uuid.uuid4())
        st.session_state.historico = []
        st.rerun()


def mostrar_passos(passos):
    if not passos:
        st.caption("Respondeu sem usar ferramentas.")
        return
    with st.expander(f"Raciocínio do agente ({len(passos)} passos)"):
        for p in passos:
            if p["tipo"] == "ação":
                st.markdown(f"**Ação:** `{p['ferramenta']}` com `{p['argumentos']}`")
            else:
                st.markdown(f"**Observação:** {p['resultado']}")


for item in st.session_state.historico:
    with st.chat_message(item["papel"]):
        st.markdown(item["texto"])
        if item["papel"] == "assistant":
            mostrar_passos(item["passos"])

if pergunta := st.chat_input("Pergunte sobre a sua viagem"):
    st.session_state.historico.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                resposta, passos = perguntar(agente, pergunta, st.session_state.conversa_id)
            except Exception as erro:  # erro do LLM (chave, cota, rede) aparece na tela em vez de quebrar
                resposta, passos = f"Deu erro ao falar com o modelo: {erro}", []
        st.markdown(resposta)
        mostrar_passos(passos)
    st.session_state.historico.append({"papel": "assistant", "texto": resposta, "passos": passos})
