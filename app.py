"""Interface do Consultor Inteligente de Carreiras em TI.

Atividade Aula 08 — Fase 3, Entrega 02.
Mantém as quatro perguntas e sua validação (Entrega 01) e integra
pontuação, recomendação, justificativas, regras e desempate ao motor Experta.
"""

import streamlit as st

from base_conhecimento import PERGUNTAS, TRILHAS
from motor_inferencia import MotorInferencia


st.set_page_config(
    page_title="Consultor de Carreiras em TI",
    page_icon="🧭",
    layout="centered",
)

st.title("Consultor Inteligente de Carreiras em TI")
st.caption("Atividade Aula 08 — Interface Streamlit")
st.write(
    "Responda às quatro perguntas para identificar seus interesses e "
    "afinidades profissionais na área de Tecnologia da Informação."
)

st.subheader("Entrevista de perfil")

respostas = {}
with st.form("formulario_entrevista"):
    for pergunta in PERGUNTAS:
        st.markdown(f"**{pergunta.numero}. {pergunta.enunciado}**")
        opcao_selecionada = st.selectbox(
            label="Escolha uma alternativa",
            options=pergunta.opcoes,
            index=None,
            placeholder="Selecione uma alternativa...",
            format_func=lambda opcao: f"{opcao.titulo} — {opcao.descricao}",
            key=f"resposta_{pergunta.dimensao}",
        )
        respostas[pergunta.dimensao] = opcao_selecionada

    enviado = st.form_submit_button(
        "Conferir respostas", type="primary", use_container_width=True
    )

if enviado:
    pendentes = [
        str(pergunta.numero)
        for pergunta in PERGUNTAS
        if respostas[pergunta.dimensao] is None
    ]
    if pendentes:
        st.warning(
            "Responda todas as perguntas antes de continuar. "
            f"Perguntas pendentes: {', '.join(pendentes)}."
        )
    else:
        st.success("As quatro respostas foram registradas na interface!")
        st.subheader("Resumo das respostas")
        for pergunta in PERGUNTAS:
            opcao = respostas[pergunta.dimensao]
            st.markdown(f"**{pergunta.numero}. {pergunta.enunciado}**")
            st.write(f"{opcao.titulo} — {opcao.descricao}")

        # Enviar ao Experta os códigos exatos aprovados na Fase 1.
        codigos = {
            dimensao: opcao.codigo for dimensao, opcao in respostas.items()
        }
        try:
            motor = MotorInferencia()
            motor.registrar_perfil(codigos)
            recomendacao = motor.recomendar_carreira()
        except (ValueError, RuntimeError) as erro:
            st.error(f"Não foi possível gerar a recomendação: {erro}")
        else:
            st.divider()
            st.subheader("Sua recomendação de carreira")
            st.success(recomendacao.nome_trilha)
            st.metric("Pontuação obtida", f"{recomendacao.pontuacao_total} pontos")

            st.markdown("**Por que esta carreira foi recomendada?**")
            for justificativa in recomendacao.justificativas_pontuacao:
                st.markdown(f"- {justificativa}")

            st.markdown("**Regras cruzadas acionadas para esta carreira**")
            if recomendacao.regras_da_trilha:
                for regra in recomendacao.regras_da_trilha:
                    st.markdown(f"- Regra {regra.numero}: {regra.motivo}")
            else:
                st.info(
                    "Nenhuma regra cruzada desta carreira foi acionada. "
                    "A recomendação foi definida pela pontuação das respostas "
                    "e, quando necessário, pelo desempate."
                )

            if recomendacao.desempate is not None:
                nomes_trilhas = {trilha.codigo: trilha.nome for trilha in TRILHAS}
                nomes_criterios = {
                    "atuacao": "preferência de atuação diária",
                    "entrega": "tipo de entrega de valor",
                    "ferramenta_principal": "afinidade com a ferramenta principal",
                    "matematica": "afinidade matemática",
                }
                dados = recomendacao.desempate
                candidatos = ", ".join(
                    nomes_trilhas[codigo] for codigo in dados.candidatos_originais
                )
                st.info(
                    f"**Desempate aplicado:** {candidatos} obtiveram "
                    f"{dados.pontuacao_empatada} pontos. "
                    f"Critério decisivo: {nomes_criterios[dados.criterio_decisivo]}."
                )

            with st.expander("Consultar a pontuação das 10 carreiras"):
                classificacao = sorted(
                    recomendacao.pontuacoes,
                    key=lambda pontos: pontos.total,
                    reverse=True,
                )
                st.table(
                    [
                        {"Carreira": pontos.nome_trilha, "Pontos": pontos.total}
                        for pontos in classificacao
                    ]
                )

            with st.expander("Ver outras regras cruzadas identificadas"):
                if recomendacao.regras_de_outras_trilhas:
                    for regra in recomendacao.regras_de_outras_trilhas:
                        st.markdown(f"- Regra {regra.numero}: {regra.motivo}")
                else:
                    st.write("Nenhuma outra regra cruzada foi acionada.")
