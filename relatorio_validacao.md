# Relatório de Validação com Personas

**Projeto:** Consultor Inteligente de Carreiras em TI  
**Atividade:** Aula 08 — Inteligência Artificial  
**Data da validação:** 22 de outubro de 2026  
**Tecnologias avaliadas:** Python, Experta e Streamlit

## 1. Objetivo

Verificar se o sistema especialista recomenda carreiras de TI de maneira coerente para quatro perfis profissionais distintos. A validação considera as quatro respostas da entrevista, a pontuação calculada, as regras cruzadas efetivamente acionadas, as justificativas exibidas e a ausência de informações herdadas de entrevistas anteriores.

## 2. Procedimentos de validação

Foram adotadas duas formas complementares de avaliação:

1. **Testes automatizados do motor:** execução do arquivo `test_personas.py`, utilizando `base_conhecimento.py` e `motor_inferencia.py`, com verificações de carreira, pontuação, parcelas, regras disparadas, justificativas e isolamento de dados.
2. **Verificação manual da interface web:** preenchimento sucessivo das quatro personas no Streamlit, por meio de `app.py`, com conferência visual das recomendações, dos pontos, das justificativas e das regras apresentadas.

Os comandos utilizados foram:

```powershell
python test_personas.py
python -m streamlit run app.py
```

Os testes foram realizados na pasta principal do projeto com o ambiente virtual Python ativo, sem alterar o código do motor durante a validação.

## 3. Personas e resultados observados

| Persona | Matemática | Preferência de atuação | Ferramenta | Tipo de resultado | Carreira recomendada | Pontuação | Regras da carreira |
|---|---|---|---|---|---|---:|---|
| Analítica | Alta | Análise de dados e modelos de IA | Python | Informações e previsões | Ciência de Dados e Machine Learning | 15 | 7, 8, 9 |
| Infraestrutura e segurança | Média | Identificação de vulnerabilidades | Linux/Redes | Proteção contra ameaças | Cibersegurança (Security / Pentesting) | 14 | 13, 14, 15 |
| Visual/front-end | Baixa | Criação de interfaces | JavaScript/TypeScript | Experiência do usuário | Desenvolvimento Front-end & UI/UX | 13 | 4, 5 |
| Negócios e produtos | Baixa | Planejamento de produtos | Jira/Trello/Figma | Estratégias e prioridades de negócio | Gestão de Produtos (Product Management) | 13 | 28, 29, 30 |

Para as quatro personas, os resultados esperados foram confirmados nos testes automatizados e nas capturas da interface Streamlit. As justificativas e as parcelas de pontuação exibidas corresponderam às respostas selecionadas.

## 4. Verificações automatizadas

| Teste | Critério de aprovação | Resultado |
|---|---|---|
| `test_quatro_personas` | As quatro personas recebem carreira, pontuação, parcelas, regras e justificativas esperadas | Aprovado |
| `test_perfil_incompleto_e_rejeitado` | Perfil sem uma dimensão obrigatória provoca `ValueError` | Aprovado |
| `test_recomendacao_exige_perfil` | Solicitar recomendação sem entrevista registrada provoca `RuntimeError` | Aprovado |
| `test_troca_de_perfil_sem_reutilizar_disparos` | Entrevistas consecutivas no mesmo motor não reutilizam regras e fatos anteriores | Aprovado |

As asserções também conferem a presença das dez carreiras na lista de pontuações, a soma dos critérios e a correspondência dos disparos às condições declaradas na base de conhecimento.

### Resultado registrado no terminal

```text
Ran 4 tests in 0.067s

OK
```

**Resultado:** quatro métodos de teste aprovados, sem falhas ou erros reportados na execução apresentada.

## 5. Verificação na interface Streamlit

As quatro personas foram preenchidas sucessivamente na interface web. Os resultados apresentados foram confrontados com os valores e as regras esperados:

| Persona | Carreira exibida | Pontuação exibida | Regras exibidas | Avaliação |
|---|---|---:|---|---|
| Analítica | Ciência de Dados e Machine Learning | 15 | 7, 8, 9 | Aprovada |
| Infraestrutura e segurança | Cibersegurança (Security / Pentesting) | 14 | 13, 14, 15 | Aprovada |
| Visual/front-end | Desenvolvimento Front-end & UI/UX | 13 | 4, 5 | Aprovada |
| Negócios e produtos | Gestão de Produtos (Product Management) | 13 | 28, 29, 30 | Aprovada |

A interface exibiu, nos cenários conferidos, a carreira recomendada, a pontuação total, os motivos individuais de pontuação e as regras cruzadas correspondentes. A sequência de entrevistas não apresentou reutilização visível da recomendação anterior.

## 6. Escopo e limitações

- Os quatro cenários foram validados pelo motor automatizado e por inspeção manual dos resultados na interface Streamlit; **não** foi executada uma suíte automatizada de testes de navegador de ponta a ponta.
- Os testes demonstram comportamento correto para os perfis selecionados, mas não garantem ausência de falhas em todas as combinações possíveis de respostas.
- A verificação manual foi baseada nas saídas apresentadas durante o uso da aplicação e nas capturas compartilhadas; não corresponde a uma auditoria independente do ambiente de execução.
- A pontuação mede compatibilidade com os critérios cadastrados na base de conhecimento, não sendo uma avaliação objetiva de aptidão profissional.

## 7. Conclusão

A validação das quatro personas foi **aprovada**. Os testes automatizados encerraram com `OK`, e as quatro verificações pela interface Streamlit apresentaram as carreiras, pontuações e regras cruzadas esperadas. Também foram aprovados os controles de perfil incompleto, recomendação sem perfil registrado e isolamento de dados entre entrevistas no motor de inferência. Os resultados atendem ao escopo de validação com quatro personas, observadas as limitações registradas acima.
