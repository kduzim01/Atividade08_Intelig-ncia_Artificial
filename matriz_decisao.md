# Matriz de decisão e catálogo de regras

**Projeto:** Consultor Inteligente de Carreiras em TI

Esta matriz foi derivada diretamente das quatro perguntas, dez carreiras e 30 regras declarativas em `base_conhecimento.py`. Serve para auditar os critérios aplicados pelo motor Experta. Não é uma segunda fonte de cálculo.

## Perguntas e alternativas

| Dimensão | Quantidade de respostas | Conteúdo |
|---|---:|---|
| Matemática | 3 | Baixa, Média, Alta |
| Atuação diária | 10 | Uma das dez áreas profissionais |
| Ferramenta | 11 | Dez grupos de ferramentas e opção Nenhuma/Iniciante |
| Entrega de valor | 10 | Um objetivo profissional para cada área |

## Matriz de pontuação por carreira

| Carreira | Matemática (pontos) | Atuação (+5) | Ferramenta principal (+3) | Ferramenta complementar (+1) | Entrega (+5) | Regras |
|---|---|---|---|---|---|---|
| Desenvolvimento Back-end | media: +1, alta: +1 | Desenvolver algoritmos, APIs e regras de negócio. | C. Java / C# | A. Python; D. SQL / Bancos de Dados | Desenvolver sistemas funcionais que resolvam problemas reais dos usuários e empresas. | 1, 2, 3 |
| Desenvolvimento Front-end & UI/UX | 0 para todas | Criar interfaces visuais e melhorar a experiência dos usuários. | B. JavaScript / TypeScript | J. Jira / Trello / Figma | Criar experiências digitais intuitivas, acessíveis e visualmente agradáveis. | 4, 5, 6 |
| Ciência de Dados e Machine Learning | media: +1, alta: +2 | Analisar dados, identificar padrões e desenvolver modelos de inteligência artificial. | A. Python | D. SQL / Bancos de Dados | Transformar dados em informações, previsões e decisões inteligentes. | 7, 8, 9 |
| Engenharia de Dados | media: +1, alta: +1 | Organizar grandes volumes de dados e construir pipelines de processamento. | D. SQL / Bancos de Dados | A. Python; F. Docker / Kubernetes / CI/CD | Garantir que grandes volumes de dados sejam organizados, integrados e disponibilizados corretamente. | 10, 11, 12 |
| Cibersegurança (Security / Pentesting) | media: +1, alta: +1 | Identificar vulnerabilidades e proteger sistemas contra ataques. | E. Linux / Redes | A. Python | Proteger informações, sistemas e usuários contra ameaças digitais. | 13, 14, 15 |
| DevOps & SRE | media: +1, alta: +1 | Automatizar processos de desenvolvimento, testes e implantação de sistemas. | F. Docker / Kubernetes / CI/CD | E. Linux / Redes; G. AWS / Azure / Google Cloud | Tornar processos tecnológicos mais rápidos, automatizados e confiáveis. | 16, 17, 18 |
| Computação em Nuvem (Cloud Architecture) | media: +1, alta: +1 | Projetar e administrar infraestruturas em nuvem. | G. AWS / Azure / Google Cloud | E. Linux / Redes; F. Docker / Kubernetes / CI/CD | Construir infraestruturas tecnológicas escaláveis, estáveis e disponíveis. | 19, 20, 21 |
| Desenvolvimento Mobile | 0 para todas | Desenvolver aplicativos para dispositivos móveis. | H. Flutter / React Native / Kotlin / Swift | B. JavaScript / TypeScript | Criar aplicativos móveis que facilitem atividades do cotidiano. | 22, 23, 24 |
| Engenharia de Qualidade e Testes (QA) | 0 para todas | Testar aplicações, identificar falhas e garantir a qualidade do software. | I. Playwright / Selenium / Cypress | A. Python; B. JavaScript / TypeScript | Garantir que sistemas funcionem corretamente, prevenindo defeitos e melhorando sua qualidade. | 25, 26, 27 |
| Gestão de Produtos (Product Management) | 0 para todas | Planejar produtos digitais, definir prioridades e coordenar necessidades de negócio. | J. Jira / Trello / Figma | Nenhuma | Desenvolver estratégias e definir prioridades para produtos digitais que atendam às necessidades dos usuários e das empresas. | 28, 29, 30 |

**Interpretação da matriz:** cada pergunta pontua no máximo uma vez para cada carreira. Ferramenta principal e complementar são exclusivas na mesma carreira. Matemática baixa nunca elimina uma carreira. A opção Nenhuma/Iniciante não pontua. A pontuação total é a soma de matemática, atuação, ferramenta e entrega.

## Catálogo das 30 regras lógicas cruzadas

As condições de uma regra são combinadas por **E**. Quando uma condição apresenta várias alternativas, basta uma delas (**OU**). Apenas as regras efetivamente disparadas pelo Experta podem ser utilizadas como evidência de desempate.

| Regra | Carreira | Condições (SE) | Tipo | Evidência registrada (ENTÃO) |
|---:|---|---|---|---|
| 1 | Desenvolvimento Back-end | **atuacao** = `logica` **E** **ferramenta** = `java` | favoravel | Interesse em algoritmos/APIs e afinidade com Java/C#. |
| 2 | Desenvolvimento Back-end | **atuacao** = `logica` **E** **entrega** = `funcionalidade` | favoravel | Interesse em algoritmos/APIs e em sistemas funcionais. |
| 3 | Desenvolvimento Back-end | **matematica** = `media` **OU** `alta` **E** **ferramenta** = `sql` **E** **entrega** = `funcionalidade` | complementar | Afinidade lógica, SQL e entrega de sistemas funcionais. |
| 4 | Desenvolvimento Front-end & UI/UX | **atuacao** = `interfaces` **E** **ferramenta** = `javascript` | favoravel | Interesse em interfaces e JavaScript/TypeScript. |
| 5 | Desenvolvimento Front-end & UI/UX | **atuacao** = `interfaces` **E** **entrega** = `experiencia` | favoravel | Interesse em interfaces e experiências acessíveis. |
| 6 | Desenvolvimento Front-end & UI/UX | **ferramenta** = `gestao` **E** **entrega** = `experiencia` | complementar | Afinidade com o grupo Jira/Trello/Figma e com experiências visuais. |
| 7 | Ciência de Dados e Machine Learning | **matematica** = `alta` **E** **atuacao** = `analise` | favoravel | Alta afinidade matemática e interesse em modelos de IA. |
| 8 | Ciência de Dados e Machine Learning | **atuacao** = `analise` **E** **entrega** = `inteligencia` | favoravel | Interesse em análise de dados e previsões. |
| 9 | Ciência de Dados e Machine Learning | **ferramenta** = `python` **E** **matematica** = `media` **OU** `alta` **E** **entrega** = `inteligencia` | complementar | Python, afinidade matemática e interesse em previsões. |
| 10 | Engenharia de Dados | **atuacao** = `engenharia_dados` **E** **ferramenta** = `sql` | favoravel | Interesse em pipelines e SQL/Bancos de Dados. |
| 11 | Engenharia de Dados | **atuacao** = `engenharia_dados` **E** **entrega** = `dados` | favoravel | Interesse em pipelines e integração/disponibilidade de dados. |
| 12 | Engenharia de Dados | **matematica** = `media` **OU** `alta` **E** **ferramenta** = `python` **OU** `devops` **E** **entrega** = `dados` | complementar | Matemática, Python ou Docker/CI-CD e integração de dados. |
| 13 | Cibersegurança (Security / Pentesting) | **atuacao** = `seguranca` **E** **ferramenta** = `redes` | favoravel | Interesse em vulnerabilidades e Linux/Redes. |
| 14 | Cibersegurança (Security / Pentesting) | **atuacao** = `seguranca` **E** **entrega** = `seguranca` | favoravel | Interesse em vulnerabilidades e proteção de sistemas. |
| 15 | Cibersegurança (Security / Pentesting) | **ferramenta** = `redes` **OU** `python` **E** **matematica** = `media` **OU** `alta` **E** **entrega** = `seguranca` | complementar | Linux/Redes ou Python, matemática e proteção digital. |
| 16 | DevOps & SRE | **atuacao** = `devops` **E** **ferramenta** = `devops` | favoravel | Interesse em automação de implantação e Docker/Kubernetes/CI-CD. |
| 17 | DevOps & SRE | **atuacao** = `devops` **E** **entrega** = `automacao` | favoravel | Interesse em automação e confiabilidade operacional. |
| 18 | DevOps & SRE | **ferramenta** = `devops` **E** **entrega** = `automacao` | complementar | Docker/Kubernetes/CI-CD e melhoria de processos. |
| 19 | Computação em Nuvem (Cloud Architecture) | **atuacao** = `cloud` **E** **ferramenta** = `cloud` | favoravel | Interesse em infraestrutura de nuvem e AWS/Azure/GCP. |
| 20 | Computação em Nuvem (Cloud Architecture) | **atuacao** = `cloud` **E** **entrega** = `infraestrutura` | favoravel | Interesse em arquitetura de nuvem e escalabilidade. |
| 21 | Computação em Nuvem (Cloud Architecture) | **ferramenta** = `redes` **OU** `devops` **E** **matematica** = `media` **OU** `alta` **E** **entrega** = `infraestrutura` | complementar | Linux/Redes ou Docker/CI-CD, matemática e escalabilidade. |
| 22 | Desenvolvimento Mobile | **atuacao** = `mobile` **E** **ferramenta** = `mobile` | favoravel | Interesse em aplicativos móveis e Flutter/React Native/Kotlin/Swift. |
| 23 | Desenvolvimento Mobile | **atuacao** = `mobile` **E** **entrega** = `mobile` | favoravel | Interesse em aplicativos móveis e soluções para o cotidiano. |
| 24 | Desenvolvimento Mobile | **ferramenta** = `javascript` **OU** `mobile` **E** **entrega** = `mobile` | complementar | JavaScript/TypeScript ou tecnologias mobile para aplicativos. |
| 25 | Engenharia de Qualidade e Testes (QA) | **atuacao** = `qa` **E** **ferramenta** = `qa` | favoravel | Interesse em testar sistemas e Playwright/Selenium/Cypress. |
| 26 | Engenharia de Qualidade e Testes (QA) | **atuacao** = `qa` **E** **entrega** = `qualidade` | favoravel | Interesse em testar aplicações e prevenir defeitos. |
| 27 | Engenharia de Qualidade e Testes (QA) | **ferramenta** = `python` **OU** `javascript` **OU** `qa` **E** **entrega** = `qualidade` | complementar | Python/JavaScript/ferramentas QA e garantia de qualidade. |
| 28 | Gestão de Produtos (Product Management) | **atuacao** = `produto` **E** **ferramenta** = `gestao` | favoravel | Interesse em planejar produtos e Jira/Trello/Figma. |
| 29 | Gestão de Produtos (Product Management) | **atuacao** = `produto` **E** **entrega** = `negocios` | favoravel | Interesse em planejar produtos e estrategia de negócio. |
| 30 | Gestão de Produtos (Product Management) | **ferramenta** = `gestao` **E** **entrega** = `negocios` | complementar | Jira/Trello/Figma e priorização de produtos digitais. |

## Política de recomendação e desempate

1. Calcular os pontos de compatibilidade para as dez carreiras. A carreira única de maior pontuação é recomendada.
2. Se duas ou mais carreiras empatam na maior pontuação, usar a contagem de **regras cruzadas realmente disparadas para cada uma das empatadas**, sem somar pontos por regra.
3. Se o empate de evidências persistir, aplicar, nesta ordem, os quatro critérios originais: **atuação profissional → entrega de valor → ferramenta principal → matemática**.
4. Se todos os critérios permanecerem iguais, sinalizar erro de ambiguidade, sem selecionar uma carreira arbitrariamente.

### Exemplo de decisão por regra

Com matemática **média**, atuação **DevOps**, ferramenta **Linux/Redes** e entrega de **infraestrutura**: DevOps e Cloud obtêm **7 pontos** cada. A regra **21**, ligada a Linux/Redes, matemática e infraestrutura, é acionada para **Cloud**. Assim, com a política revisada, Cloud vence o desempate **por evidência de regra**, mantendo os 7 pontos. O resultado difere da política anterior, na qual a preferência de atuação favorecia DevOps.

### Limites e rastreabilidade

- Não disparar regra não impede uma recomendação: os critérios individuais ainda calculam compatibilidade em todos os perfis.
- O Experta registra as regras cruzadas utilizadas como evidência; a pontuação ponderada e o desempate completam a decisão.
- Esta matriz descreve a política implementada, não é uma avaliação objetiva de aptidão profissional.
- Alterações nas respostas, pesos ou condições do código exigem atualização correspondente desta tabela e reexecução dos testes.
