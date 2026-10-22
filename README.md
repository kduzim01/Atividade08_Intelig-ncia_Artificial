# Consultor Inteligente de Carreiras em TI

Sistema especialista baseado em regras que auxilia na identificação de uma trilha profissional em Tecnologia da Informação a partir das preferências e afinidades informadas pelo usuário. Projeto acadêmico da disciplina de Inteligência Artificial, desenvolvido no contexto da UNIPAC.

A aplicação apresenta uma entrevista com quatro perguntas, calcula a compatibilidade com dez carreiras e explica a recomendação utilizando pontuação, regras de inferência e critérios de desempate.

## Funcionalidades

- Entrevista com quatro dimensões: afinidade matemática, preferência de atuação profissional, ferramenta ou linguagem de maior afinidade e tipo de entrega de valor.
- Validação de todas as respostas obrigatórias.
- Motor de inferência com **30 regras cruzadas** implementadas com a biblioteca **Experta**.
- Pontuação das **dez trilhas profissionais** conforme a matriz de decisão cadastrada.
- Desempate em duas camadas: primeiro pelas evidências das regras efetivamente disparadas; persistindo a igualdade, atuação profissional, entrega de valor, ferramenta principal e afinidade matemática.
- Recomendação acompanhada de justificativas de pontuação e identificação das regras efetivamente disparadas.
- Consulta às pontuações das dez carreiras e às regras adicionais identificadas.
- Interface web construída com Streamlit.

## Trilhas de carreira

1. Desenvolvimento Back-end
2. Desenvolvimento Front-end & UI/UX
3. Ciência de Dados e Machine Learning
4. Engenharia de Dados
5. Cibersegurança (Security / Pentesting)
6. DevOps & SRE
7. Computação em Nuvem (Cloud Architecture)
8. Desenvolvimento Mobile
9. Engenharia de Qualidade e Testes (QA)
10. Gestão de Produtos (Product Management)

## Tecnologias

- **Python 3.12** — linguagem utilizada no desenvolvimento e na validação local.
- **Experta 1.9.4** — mecanismo de regras do tipo SE–ENTÃO e processamento de fatos.
- **Streamlit 1.66.1** — interface web interativa.
- **unittest** — testes automatizados, disponível na biblioteca padrão do Python.
- **Git e GitHub** — controle de versão.

O ambiente utilizado na validação foi Windows com PowerShell e ambiente virtual Python. O projeto utiliza uma adaptação de compatibilidade no `motor_inferencia.py` para o uso da dependência `frozendict` da versão de Experta adotada com Python 3.12.

## Estrutura do projeto

```text
.
├── app.py                   # Interface web Streamlit
├── base_conhecimento.py     # Perguntas, trilhas, regras e pesos
├── motor_inferencia.py      # Motor Experta, pontuação e recomendações
├── test_personas.py         # Testes automatizados das personas
├── relatorio_validacao.md   # Resultados e limitações da validação
├── matriz_decisao.md       # Matriz de pontuação e catálogo de 30 regras
├── requirements.txt         # Dependências Python
├── README.md                # Documentação principal
└── .gitignore               # Arquivos ignorados pelo Git
```

As pastas locais `.venv/` e `__pycache__/` não precisam ser incluídas no repositório.

## Instalação

Requisitos: Python 3.12, Git e acesso a um terminal. Os comandos abaixo usam PowerShell no Windows.

1. Clone o repositório e entre na pasta do projeto:

   ```powershell
   git clone https://github.com/kduzim01/Atividade08_Intelig-ncia_Artificial.git
   cd Atividade08_Intelig-ncia_Artificial
   ```

2. Crie e ative o ambiente virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Se a ativação for bloqueada pela política de execução do PowerShell, pode-se habilitá-la apenas na sessão atual e tentar novamente:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:

   ```powershell
   python -m pip install -r requirements.txt
   ```

## Executar a aplicação

Com o ambiente virtual ativo, na pasta principal do projeto:

```powershell
python -m streamlit run app.py
```

Abra o endereço local exibido no terminal (geralmente `http://localhost:8501`). Selecione uma alternativa em cada uma das quatro perguntas e clique em **Conferir respostas** para visualizar a carreira recomendada, sua pontuação e as justificativas.

Para encerrar o servidor, utilize `Ctrl + C` no terminal.

## Executar os testes automatizados

Com o ambiente virtual ativo, execute:

```powershell
python test_personas.py
```

Alternativamente:

```powershell
python -m unittest -v test_personas.py
```

A suíte automatizada verifica quatro personas, perfis completos das dez carreiras, diferenciação entre Ciência de Dados e Engenharia de Dados, desempates com e sem regras disparadas, cenários de ativação das 30 regras, rejeição de perfis incompletos e isolamento entre entrevistas. **Após a refatoração, os 9 testes passaram com Experta no ambiente de desenvolvimento (1,366 segundo, sem falhas).** O conjunto anterior tinha 4 testes, também aprovados.

Os resultados das quatro personas originais, os testes ampliados, os cenários da refatoração e as limitações estão em [`relatorio_validacao.md`](relatorio_validacao.md). A validação registrada compreende testes automatizados do motor e verificações manuais na interface, não uma suíte automatizada de ponta a ponta no navegador.

## Como a recomendação é calculada

A base de conhecimento define quatro respostas, dez trilhas, pesos e 30 regras cruzadas. O motor Experta executa as regras e registra as condições realmente atendidas, enquanto a matriz calcula a pontuação de cada carreira. As regras **não aumentam nem duplicam os pontos**.

A decisão segue a política:

1. Selecionar a carreira com **maior pontuação**; se houver apenas uma, ela é recomendada.
2. Se houver empate na maior pontuação, comparar **quantas regras cruzadas do Experta foram disparadas para cada carreira empatada**. Vence a que possuir mais evidências, desde que não haja novo empate.
3. Persistindo o empate de evidências (inclusive quando nenhuma regra disparou), aplicar os critérios ordenados: **atuação → entrega → ferramenta principal → matemática**.
4. Se todos os critérios ainda coincidirem, informar erro explícito, em vez de selecionar arbitrariamente uma carreira.

Exemplo de decisão revisada: matemática média, atuação DevOps, Linux/Redes e entrega de infraestrutura produzem **7 pontos tanto para DevOps & SRE quanto para Cloud Architecture**. A regra 21 de Cloud é disparada, decidindo o empate a favor de **Cloud Architecture**, sem alterar a pontuação. Na política anterior, a atuação favorecia DevOps. **O novo resultado foi confirmado na interface Streamlit após a refatoração.**

A interface distingue **justificativas de pontuação**, **regras cruzadas disparadas** e **critério decisivo do desempate**. Quando nenhuma regra da carreira recomendada foi ativada, isso é mostrado explicitamente. A [matriz de decisão](matriz_decisao.md) detalha todas as carreiras, pesos e regras.

## Escopo e limitações

Esta é uma ferramenta acadêmica de apoio à exploração de carreiras, não uma avaliação psicológica ou profissional definitiva. As recomendações dependem das alternativas e dos pesos definidos na base de conhecimento. Os cenários validados não garantem cobertura exaustiva de todas as combinações possíveis de respostas.


## Validação e reprodução dos testes

A refatoração foi verificada no ambiente de desenvolvimento com **9 testes automatizados aprovados com Experta real**. Na interface Streamlit, foram conferidos os seguintes cenários após a mudança:

| Cenário | Resultado confirmado | Regras da carreira recomendada |
|---|---|---|
| Empate DevOps/Cloud | Cloud Architecture — 7 pontos, desempate por evidência | 21 |
| Engenharia de Dados | Engenharia de Dados — 14 pontos | 10 e 11 |
| Ciência de Dados e Machine Learning | Ciência de Dados e Machine Learning — 15 pontos | 7, 8 e 9 |

As quatro personas originais também foram validadas na versão anterior da interface e permanecem cobertas pelos testes automatizados da versão refatorada. **Não foi realizada uma nova conferência manual de todas as quatro personas após a mudança.**

Para reproduzir os testes no ambiente Python configurado, execute:

```powershell
python base_conhecimento.py
python motor_inferencia.py
python -m unittest -v test_personas.py
python -m streamlit run app.py
```

Após iniciar o Streamlit, confira os resultados no navegador. Em outro computador ou após novas alterações, execute novamente os testes e atualize o [relatório de validação](relatorio_validacao.md) com os resultados observados. Os cenários aprovados não constituem teste exaustivo das 3.300 combinações possíveis nem automação de navegador de ponta a ponta.
