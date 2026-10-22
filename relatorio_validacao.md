# Relatório de Validação com Personas

**Projeto:** Consultor Inteligente de Carreiras em TI  
**Atividade:** Aula 08 — Inteligência Artificial  
**Data da validação:** 22 de outubro de 2026  
**Tecnologias avaliadas:** Python, Experta e Streamlit

## 1. Objetivo

Verificar se o sistema especialista recomenda carreiras de Tecnologia da Informação de maneira coerente para perfis profissionais distintos, considerando as quatro respostas da entrevista, as pontuações calculadas, as regras cruzadas efetivamente acionadas, as justificativas apresentadas e o isolamento de dados entre entrevistas. Também verificar a política de desempate revisada e a diferenciação entre carreiras com competências próximas.

## 2. Procedimentos de validação

Foram utilizadas duas modalidades complementares de avaliação:

1. **Testes automatizados do motor:** execução de `test_personas.py` utilizando a base de conhecimento e o motor de inferência com a biblioteca Experta instalada. Os testes verificam carreiras, pontuação, parcelas, regras disparadas, justificativas, desempates e integridade dos perfis.
2. **Verificação manual na interface web:** preenchimento de perfis na aplicação Streamlit, com inspeção das carreiras recomendadas, das pontuações, das regras e das mensagens explicativas.

Os comandos utilizados foram:

```powershell
python test_personas.py
python -m unittest -v test_personas.py
python -m streamlit run app.py
```

As validações foram realizadas no ambiente virtual Python do projeto. Os resultados da execução original e os resultados posteriores à refatoração são distinguidos nas próximas seções.

## 3. Personas originalmente validadas

| Persona | Matemática | Preferência de atuação | Ferramenta | Tipo de resultado | Carreira recomendada | Pontuação | Regras da carreira |
|---|---|---|---|---|---|---:|---|
| Analítica | Alta | Análise de dados e modelos de IA | Python | Informações e previsões | Ciência de Dados e Machine Learning | 15 | 7, 8, 9 |
| Infraestrutura e segurança | Média | Identificação de vulnerabilidades | Linux/Redes | Proteção contra ameaças | Cibersegurança (Security / Pentesting) | 14 | 13, 14, 15 |
| Visual/front-end | Baixa | Criação de interfaces | JavaScript/TypeScript | Experiência do usuário | Desenvolvimento Front-end & UI/UX | 13 | 4, 5 |
| Negócios e produtos | Baixa | Planejamento de produtos | Jira/Trello/Figma | Estratégias e prioridades de negócio | Gestão de Produtos (Product Management) | 13 | 28, 29, 30 |

As quatro personas produziram as carreiras, pontuações e regras esperadas nos testes automatizados e nas verificações manuais realizadas durante a validação original. Após a refatoração, os mesmos quatro perfis também passaram no teste automatizado correspondente.

### Registro da execução original

O conjunto inicial incluía quatro métodos de teste: validação das quatro personas, rejeição de perfil incompleto, exigência de perfil registrado e ausência de reutilização de fatos e disparos entre entrevistas.

```text
Ran 4 tests in 0.067s

OK
```

Esse registro é **histórico** e não representa a quantidade de testes da versão refatorada.

## 4. Verificações automatizadas após a refatoração

O arquivo `test_personas.py` foi ampliado para nove métodos de teste, mantendo os cenários originais e acrescentando verificações da nova política de inferência.

| Teste | Critério de aprovação | Resultado |
|---|---|---|
| `test_quatro_personas` | Recomendar corretamente as quatro personas, com pontos, regras e justificativas | Aprovado |
| `test_troca_de_perfil_sem_reutilizar_disparos` | Não reutilizar fatos ou regras entre entrevistas consecutivas | Aprovado |
| `test_diferenciacao_entre_ciencia_e_engenharia_de_dados` | Distinguir análise e previsão de pipelines e integração de dados | Aprovado |
| `test_dez_trilhas_com_perfis_completos` | Permitir recomendar cada uma das dez carreiras com um perfil alinhado | Aprovado |
| `test_regras_de_inferencia_podem_decidir_empate` | Usar a Regra 21 para desempatar Cloud e DevOps, mantendo 7 pontos | Aprovado |
| `test_empate_sem_disparos_preserva_preferencia_de_atuacao` | Manter a preferência de atuação como desempate quando não há evidência de regras | Aprovado |
| `test_todas_as_regras_possuem_um_cenario_de_disparo` | Confirmar um perfil capaz de acionar cada uma das 30 regras do Experta | Aprovado |
| `test_recomendacao_exige_perfil` | Impedir recomendação sem perfil registrado | Aprovado |
| `test_perfil_incompleto_e_rejeitado` | Rejeitar entrevista com dimensão obrigatória ausente | Aprovado |

### Resultado registrado no terminal

```text
Ran 9 tests in 1.366s

OK
```

**Resultado:** nove métodos de teste aprovados, sem falhas ou erros reportados na execução apresentada. Os testes foram executados no ambiente de desenvolvimento com a biblioteca Experta instalada. O resultado comprova os cenários verificados, não todas as combinações possíveis de entrevistas.

## 5. Verificação manual na interface Streamlit

### 5.1. Quatro personas originais

| Persona | Carreira exibida | Pontuação exibida | Regras exibidas | Avaliação |
|---|---|---:|---|---|
| Analítica | Ciência de Dados e Machine Learning | 15 | 7, 8, 9 | Aprovada na validação original |
| Infraestrutura e segurança | Cibersegurança (Security / Pentesting) | 14 | 13, 14, 15 | Aprovada na validação original |
| Visual/front-end | Desenvolvimento Front-end & UI/UX | 13 | 4, 5 | Aprovada na validação original |
| Negócios e produtos | Gestão de Produtos (Product Management) | 13 | 28, 29, 30 | Aprovada na validação original |

Os quatro perfis foram executados em sequência na interface, sem reutilização visível da recomendação anterior. Após a refatoração, os quatro perfis permaneceram cobertos pelo teste automatizado, mas não foi registrada uma nova rodada manual completa dessas quatro personas.

### 5.2. Cenários adicionais da refatoração

Os cenários abaixo foram executados manualmente na interface Streamlit **após a alteração da política de desempate**.

| Cenário | Resultado observado | Regras exibidas | Avaliação |
|---|---|---|---|
| Empate DevOps/Cloud | Computação em Nuvem (Cloud Architecture) — 7 pontos | 21 | Aprovado |
| Engenharia de Dados | Engenharia de Dados — 14 pontos | 10 e 11 | Aprovado |
| Ciência de Dados e Machine Learning | Ciência de Dados e Machine Learning — 15 pontos | 7, 8 e 9 | Aprovado |

No cenário DevOps/Cloud, as duas carreiras obtiveram **7 pontos**. A interface indicou que o critério decisivo foi a **quantidade de regras cruzadas disparadas**: a Regra 21 forneceu evidência para Computação em Nuvem, sem alterar a pontuação ponderada. Nos dois cenários de dados, o sistema diferenciou corretamente a criação de modelos preditivos da construção de pipelines de processamento.

## 6. Política de recomendação e desempate

A pontuação de cada carreira continua sendo calculada a partir das respostas e dos pesos declarados na base de conhecimento. O disparo de regras Experta não acrescenta pontos nem duplica parcelas da pontuação.

A política revisada segue esta ordem:

1. Recomendar a carreira com maior pontuação quando houver uma única vencedora.
2. Se duas ou mais carreiras empatarem na maior pontuação, comparar a quantidade de regras cruzadas **efetivamente disparadas** para cada carreira empatada.
3. Se a quantidade de regras não resolver o empate, aplicar, nesta ordem, os critérios originais: **atuação profissional, entrega de valor, ferramenta principal e afinidade matemática**.
4. Se todos os critérios permanecerem iguais, sinalizar a impossibilidade de desempate, sem selecionar arbitrariamente uma carreira.

O cenário validado de DevOps/Cloud confirma que as regras podem participar da escolha final em caso de empate. A aplicação permanece um sistema acadêmico híbrido, combinando matriz de pontuação e evidências de inferência baseadas em regras.

## 7. Análise estática complementar

A enumeração das alternativas das quatro perguntas resulta em **3.300 combinações possíveis** (3 × 10 × 11 × 10). Uma análise local, com simulação declarativa das condições das regras e comparação entre as políticas de desempate, identificou **61 combinações em que a carreira vencedora muda** e **nenhum empate sem resolução nessa simulação**.

Também foi realizada uma conferência estática de correspondência entre as 30 regras declarativas e suas condições nos decoradores `@Rule`.

**Importante:** a análise combinatória é uma simulação complementar. Ela **não representa 3.300 entrevistas executadas com a biblioteca Experta**, nem testes automatizados de navegador.

## 8. Escopo e limitações

- Os nove testes automatizados foram executados com o motor real, mas não demonstram ausência de falhas em todas as combinações de respostas.
- A verificação manual no Streamlit foi baseada nas saídas visualizadas e nas capturas apresentadas; não corresponde a uma suíte automatizada de ponta a ponta no navegador.
- As quatro personas originais foram verificadas manualmente antes da refatoração e cobertas por testes automatizados após a refatoração. Os três novos cenários foram verificados manualmente após a mudança.
- A simulação das 3.300 combinações é independente da execução real do Experta e deve ser interpretada somente como análise estática complementar.
- Os pesos e critérios representam uma matriz acadêmica de compatibilidade com carreiras, não uma avaliação objetiva ou definitiva de aptidão profissional.

## 9. Conclusão

A refatoração foi **aprovada nos cenários testados**. Os nove métodos de teste automatizados encerraram com `OK`, e as verificações adicionais no Streamlit confirmaram a aplicação do desempate por evidências de regras, a preservação da pontuação e a diferenciação entre Ciência de Dados e Engenharia de Dados.

A base mantém dez carreiras e 30 regras cruzadas, com rastreabilidade das evidências efetivamente disparadas. O relatório preserva os resultados históricos e distingue os testes com Experta dos levantamentos estáticos, evitando apresentar simulações como execuções reais.

O conjunto de validações atende ao escopo acadêmico verificado, respeitadas as limitações descritas acima.
