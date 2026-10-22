"""Interface Streamlit do Consultor Inteligente de Carreiras em TI.

Exibe a entrevista, a classificação ponderada, a recomendação rastreável,
as regras acionadas e a justificativa do desempate quando aplicável.
"""

import streamlit as st

from base_conhecimento import PERGUNTAS, TRILHAS
from motor_inferencia import MotorInferencia


st.set_page_config(
    page_title="Consultor de Carreiras em TI",
    page_icon="🧭",
    layout="centered",
)

# Identidade visual concentrada neste arquivo. Não modifica o tema global
# do Streamlit nem depende de imagens, fontes externas ou novas bibliotecas.
st.markdown(
    """
    <style>
      .career-hero {
        background: linear-gradient(115deg, #112837 0%, #174940 100%);
        border: 1px solid #34645f;
        border-radius: 18px;
        padding: 1.75rem 1.9rem;
        margin-bottom: 1.3rem;
        color: #f8fafc;
      }
      .career-hero .career-eyebrow {
        color: #99f6e4;
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .11em;
        text-transform: uppercase;
        margin-bottom: .5rem;
      }
      .career-hero h1 {
        color: #ffffff;
        font-size: clamp(1.6rem, 4vw, 2.25rem);
        line-height: 1.2;
        margin: 0 0 .65rem;
        font-weight: 740;
      }
      .career-hero p {
        color: #deeee9;
        font-size: .98rem;
        line-height: 1.55;
        margin: 0;
      }
      .career-step {
        color: #0d9488;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .09em;
        text-transform: uppercase;
      }
      .career-note {
        border-left: 3px solid #0d9488;
        padding: .5rem .9rem;
        margin: .75rem 0 1rem;
        background: color-mix(in srgb, #0d9488 9%, transparent);
        border-radius: 0 8px 8px 0;
      }
      .career-note p { margin: 0; font-size: .92rem; }
      .career-result-label {
        color: #0d9488;
        font-size: .8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .09em;
      }
      .stFormSubmitButton button[kind="primary"] {
        background-color: #0f766e;
        border-color: #0f766e;
        color: white;
        font-weight: 700;
      }
      .stFormSubmitButton button[kind="primary"]:hover {
        background-color: #115e59;
        border-color: #115e59;
        color: white;
      }
      @media (max-width: 640px) {
        .career-hero { padding: 1.25rem 1.1rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="career-hero">
      <div class="career-eyebrow">Atividade Aula 08 · Inteligência Artificial</div>
      <h1>Consultor Inteligente de Carreiras em TI</h1>
      <p>Descubra qual das dez trilhas profissionais mais combina com suas
      afinidades, interesses e objetivos. Responda a quatro perguntas e
      conheça os motivos da recomendação.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="career-step">Etapa 01 · Conhecendo seu perfil</div>', unsafe_allow_html=True)
st.subheader("Entrevista de perfil")
st.caption("São 4 perguntas. Todas as respostas são obrigatórias para gerar o resultado.")

respostas = {}
with st.form("formulario_entrevista"):
    for pergunta in PERGUNTAS:
        with st.container(border=True):
            st.markdown(
                f'<div class="career-step">Pergunta {pergunta.numero:02d} / 04</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"**{pergunta.enunciado}**")
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
        with st.expander("Revisar minhas respostas", expanded=False):
            for pergunta in PERGUNTAS:
                opcao = respostas[pergunta.dimensao]
                st.markdown(f"**{pergunta.numero}. {pergunta.enunciado}**")
                st.write(f"{opcao.titulo} — {opcao.descricao}")

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
            st.markdown(
                '<div class="career-step">Etapa 02 · Resultado da entrevista</div>',
                unsafe_allow_html=True,
            )
            st.subheader("Sua recomendação de carreira")
            with st.container(border=True):
                st.markdown(
                    '<div class="career-result-label">Trilha recomendada</div>',
                    unsafe_allow_html=True,
                )
                st.success(recomendacao.nome_trilha)
                st.metric("Pontuação obtida", f"{recomendacao.pontuacao_total} pontos")

            st.markdown("#### Por que esta carreira foi recomendada?")
            for justificativa in recomendacao.justificativas_pontuacao:
                st.markdown(f"- {justificativa}")

            st.markdown("#### Regras cruzadas acionadas para esta carreira")
            if recomendacao.regras_da_trilha:
                for regra in recomendacao.regras_da_trilha:
                    st.markdown(f"- **Regra {regra.numero}:** {regra.motivo}")
            else:
                st.info(
                    "Nenhuma regra cruzada desta carreira foi acionada. "
                    "A recomendação foi definida pela pontuação das respostas "
                    "e, quando necessário, pelo desempate."
                )

            if recomendacao.desempate is not None:
                nomes_trilhas = {trilha.codigo: trilha.nome for trilha in TRILHAS}
                nomes_criterios = {
                    "regras_cruzadas": "quantidade de regras cruzadas disparadas",
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
                        st.markdown(f"- **Regra {regra.numero}:** {regra.motivo}")
                else:
                    st.write("Nenhuma outra regra cruzada foi acionada.")

st.caption("Consultor de Carreiras em TI · Projeto acadêmico baseado em regras · UNIPAC")
