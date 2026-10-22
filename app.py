"""Interface inicial do Consultor Inteligente de Carreiras em TI.

Atividade Aula 08.
Exibe as quatro perguntas cadastradas na base de conhecimento.
A integração com a recomendação do motor Experta pertence à Entrega 02.
"""

import streamlit as st

from base_conhecimento import PERGUNTAS


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
        st.info(
            "A recomendação de carreira será entregue a próxima etapa."
        )
