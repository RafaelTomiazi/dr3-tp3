# Resultados dos casos de uso

Rodado em 23/11/2026 22:27 com o modelo gemini-3.8-flash (Google), pelo script `casos_de_uso.py`.

## 1. Clima (tool previsao_tempo)

**Pergunta:** Vou para Lisboa daqui a 2 dias e fico 3 dias. Preciso levar casaco ou guarda-chuva?

**Ferramentas usadas:** previsao_tempo

> Observação (previsao_tempo): Previsão para Lisboa (Portugal):
> - 2026-11-24: mínima 10.9°C, máxima 17.6°C, chance de chuva 88%
> - 2026-11-25: mínima 11.5°C, máxima 16.1°C, chance de chuva 6%
> - 2026-11-26: mínima 10.1°C, máxima 17.8°C, chance de chuva 5%
> - 2026-11-27: mínima 11.8°C, máxima 17.3°C, chance de chuva 10%
> - 2026-11-28: mínima 11.1°C, máxima 17.0°C, chance de chuva 20%

**Resposta:** **Sim, leve casaco, mas o guarda-chuva é pouco provável de ser necessário.**

Para o período da sua estadia (daqui a 2 dias, durante 3 dias):
- **Temperaturas:** mínimas em torno de 10°C a 12°C e máximas entre 17°C e 18°C. Vale levar um casaco moderado para as manhãs e noites.
- **Chuva:** probabilidade baixa, variando entre 5% e 20%. Dificilmente vai chover.

## 2. Câmbio (tool converter_moeda)

**Pergunta:** Tenho 3000 reais para a viagem. Quanto isso dá em euro hoje?

**Ferramentas usadas:** converter_moeda

> Observação (converter_moeda): 3000.00 BRL = 457.23 EUR (cotação de 2026-11-23: 1 BRL = 0.1524 EUR).

**Resposta:** Hoje, **R$ 3.000,00 equivalem a cerca de 457,23 €** (cotação de 1 BRL = 0,1524 EUR).

## 3. Memória + duas tools

**Pergunta:** E se eu ficar 5 dias em vez de 3, quanto posso gastar por dia em euro?

**Ferramentas usadas:** orcamento_diario

> Observação (orcamento_diario): 457.23 em 5 dias = 91.45 por dia.

**Resposta:** Ficando 5 dias com esse orçamento total (457,23 €), você poderá gastar **aproximadamente 91,45 € por dia**.

## 4. Memória pura

**Pergunta:** Para onde eu disse que vou e com quanto dinheiro?

**Ferramentas usadas:** nenhuma

**Resposta:** Você vai para **Lisboa** com um orçamento de **R$ 3.000,00** (cerca de **457,23 €**).

## 5. Erro tratado

**Pergunta:** Qual a previsão do tempo em Cidadeinexistenteabc?

**Ferramentas usadas:** previsao_tempo

> Observação (previsao_tempo): Não encontrei a cidade 'Cidadeinexistenteabc'. Peça ao usuário para conferir o nome.

**Resposta:** Não consegui encontrar informações para a cidade "Cidadeinexistenteabc". 

Por favor, verifique a grafia ou informe o nome de outra cidade para que eu possa consultar a previsão do tempo para você.
