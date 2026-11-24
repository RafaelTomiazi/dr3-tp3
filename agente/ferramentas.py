# Ferramentas (tools) que o agente pode usar.
# As duas usam APIs publicas e gratuitas, sem chave:
#   - Open-Meteo: previsao do tempo (https://open-meteo.com)
#   - Frankfurter: cotacao de moedas do Banco Central Europeu (https://frankfurter.dev)
# O texto da docstring de cada tool e o que o LLM le pra decidir quando usar,
# por isso escrevi explicando bem o que entra e o que sai.

import requests
from langchain_core.tools import tool

TIMEOUT = 10  # segundos, pra API lenta nao travar o agente


def _get_json(url, params):
    # funcao comum: faz o GET e devolve o json, ou levanta erro com mensagem clara
    resposta = requests.get(url, params=params, timeout=TIMEOUT)
    resposta.raise_for_status()
    return resposta.json()


@tool
def previsao_tempo(cidade: str, dias: int = 3) -> str:
    """Previsão do tempo de uma cidade para os próximos dias (1 a 7).
    Use quando o usuário perguntar sobre clima, temperatura, chuva ou o que levar na mala.
    Entrada: nome da cidade (ex.: 'Lisboa') e quantos dias. Saída: mínima, máxima e chance de chuva por dia."""
    dias = max(1, min(int(dias), 7))
    try:
        # 1) descobre a latitude/longitude da cidade
        geo = _get_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": cidade, "count": 1, "language": "pt"},
        )
        if not geo.get("results"):
            return f"Não encontrei a cidade '{cidade}'. Peça ao usuário para conferir o nome."
        lugar = geo["results"][0]
        # 2) pega a previsao diaria nesse ponto
        prev = _get_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": lugar["latitude"],
                "longitude": lugar["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": dias,
            },
        )["daily"]
    except requests.RequestException as erro:
        return f"Erro ao consultar a previsão do tempo: {erro}"

    linhas = [f"Previsão para {lugar['name']} ({lugar.get('country', '')}):"]
    for data, tmin, tmax, chuva in zip(
        prev["time"], prev["temperature_2m_min"], prev["temperature_2m_max"], prev["precipitation_probability_max"]
    ):
        linhas.append(f"- {data}: mínima {tmin}°C, máxima {tmax}°C, chance de chuva {chuva}%")
    return "\n".join(linhas)


@tool
def converter_moeda(valor: float, de: str, para: str) -> str:
    """Converte um valor entre moedas usando a cotação do dia (Banco Central Europeu).
    Use códigos de 3 letras: BRL (real), USD (dólar), EUR (euro), GBP (libra), ARS não é suportado.
    Entrada: valor, moeda de origem e moeda de destino. Saída: valor convertido e a cotação usada."""
    de, para = de.upper().strip(), para.upper().strip()
    if valor < 0:
        return "O valor não pode ser negativo."
    if de == para:
        return f"{valor:.2f} {de} = {valor:.2f} {para} (mesma moeda)."
    try:
        dados = _get_json("https://api.frankfurter.dev/v1/latest", {"base": de, "symbols": para})
    except requests.RequestException as erro:
        return f"Erro ao consultar a cotação ({de}->{para}): {erro}. Confira se os códigos das moedas existem."
    taxa = dados["rates"][para]
    return f"{valor:.2f} {de} = {valor * taxa:.2f} {para} (cotação de {dados['date']}: 1 {de} = {taxa:.4f} {para})."


@tool
def orcamento_diario(total: float, dias: int) -> str:
    """Divide um orçamento total pelo número de dias da viagem.
    Use quando o usuário quiser saber quanto pode gastar por dia. Entrada: total (na moeda que quiser) e dias."""
    if dias <= 0:
        return "O número de dias precisa ser maior que zero."
    return f"{total:.2f} em {dias} dias = {total / dias:.2f} por dia."


FERRAMENTAS = [previsao_tempo, converter_moeda, orcamento_diario]
