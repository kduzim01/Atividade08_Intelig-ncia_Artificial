# Consultor Inteligente de Carreiras em TI

Sistema especialista baseado em regras que auxilia na identificação de uma trilha profissional em Tecnologia da Informação a partir das preferências e afinidades informadas pelo usuário. Projeto acadêmico da disciplina de Inteligência Artificial, desenvolvido no contexto da UNIPAC.

A aplicação apresenta uma entrevista com quatro perguntas, calcula a compatibilidade com dez carreiras e explica a recomendação utilizando pontuação, regras de inferência e critérios de desempate.

## Funcionalidades

- Entrevista com quatro dimensões: afinidade matemática, preferência de atuação profissional, ferramenta ou linguagem de maior afinidade e tipo de entrega de valor.
- Validação de todas as respostas obrigatórias.
- Motor de inferência com **30 regras cruzadas** implementadas com a biblioteca **Experta**.
- Pontuação das **dez trilhas profissionais** conforme a matriz de decisão cadastrada.
- Resolução de empates por critérios ordenados: atuação profissional, entrega de valor, ferramenta principal e afinidade matemática.
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

A suíte valida quatro personas (analítica, infraestrutura e segurança, visual/front-end e negócios/produtos), além da rejeição de perfis incompletos, exigência de entrevista para recomendar e isolamento de informações entre entrevistas. A execução documentada encerrou com **4 testes aprovados**.

Os resultados detalhados, as carreiras, as pontuações e as limitações dos testes estão em [`relatorio_validacao.md`](relatorio_validacao.md). A validação registrada compreende testes automatizados do motor e verificações manuais na interface, não uma suíte automatizada de ponta a ponta no navegador.

## Como a recomendação é calculada

A base de conhecimento define respostas, trilhas, pesos e condições das 30 regras. O motor calcula a pontuação de cada carreira a partir das quatro respostas; a quantidade de regras disparadas **não multiplica a pontuação**. Quando há empate na maior pontuação, os quatro critérios de desempate são aplicados na ordem cadastrada.

A apresentação distingue as **justificativas de pontuação** das **regras cruzadas efetivamente acionadas**. Portanto, uma carreira pode ser recomendada pela pontuação e pelo desempate mesmo que nenhuma regra cruzada própria tenha disparado; essa situação é informada ao usuário.

## Escopo e limitações

Esta é uma ferramenta acadêmica de apoio à exploração de carreiras, não uma avaliação psicológica ou profissional definitiva. As recomendações dependem das alternativas e dos pesos definidos na base de conhecimento. Os cenários validados não garantem cobertura exaustiva de todas as combinações possíveis de respostas.
