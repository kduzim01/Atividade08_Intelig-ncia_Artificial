"""Base declarativa do Consultor Inteligente de Carreiras em TI.

Contém as quatro perguntas, as dez trilhas, a matriz de pontuação, as trinta
regras cruzadas, a ordem de desempate e verificações de integridade dos dados.
Não realiza processamento de fatos nem renderiza a interface web.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Opcao:
    """Alternativa de uma pergunta."""

    codigo: str
    titulo: str
    descricao: str


@dataclass(frozen=True)
class Pergunta:
    """Pergunta objetiva e dimensão correspondente do perfil."""

    numero: int
    dimensao: str
    enunciado: str
    opcoes: tuple[Opcao, ...]


@dataclass(frozen=True)
class Trilha:
    """Perfil de carreira e seus critérios de pontuação aprovados.

    O dicionário ``matematica`` associa alternativas aos respectivos pontos.
    Alternativas ausentes recebem zero ponto, sem eliminar uma carreira.
    """

    codigo: str
    nome: str
    descricao: str
    matematica: dict[str, int]
    atuacao: str
    ferramentas_principais: tuple[str, ...]
    ferramentas_complementares: tuple[str, ...]
    entrega: str


@dataclass(frozen=True)
class Condicao:
    """Uma dimensão deve corresponder a UM dos valores indicados (OU)."""

    dimensao: str
    valores: tuple[str, ...]


@dataclass(frozen=True)
class Regra:
    """Regra declarativa: TODAS as condições devem ser verdadeiras (E).

    As condições são dados declarativos espelhados nas regras do motor
    Experta, que registra os disparos efetivamente realizados.
    """

    numero: int
    trilha: str
    tipo: str
    motivo: str
    condicoes: tuple[Condicao, ...]


def _regra(
    numero: int,
    trilha: str,
    tipo: str,
    motivo: str,
    **criterios: str | tuple[str, ...],
) -> Regra:
    """Monta declarações SE-ENTÃO; não avalia respostas do usuário."""

    condicoes = tuple(
        Condicao(
            dimensao=dimensao,
            valores=valor if isinstance(valor, tuple) else (valor,),
        )
        for dimensao, valor in criterios.items()
    )
    return Regra(numero, trilha, tipo, motivo, condicoes)


# ---------------------------------------------------------------------------
# 1. ENTREVISTA - QUATRO PERGUNTAS APROVADAS
# ---------------------------------------------------------------------------
PERGUNTAS: tuple[Pergunta, ...] = (
    Pergunta(
        1,
        "matematica",
        "Qual é o seu nível de afinidade com matemática, estatística e raciocínio lógico?",
        (
            Opcao("baixa", "Baixa", "Prefiro atividades que não envolvam cálculos ou análises matemáticas frequentes."),
            Opcao("media", "Média", "Tenho facilidade com raciocínio lógico e consigo trabalhar com cálculos quando necessário."),
            Opcao("alta", "Alta", "Gosto de matemática, estatística, análise numérica e resolução de problemas complexos."),
        ),
    ),
    Pergunta(
        2,
        "atuacao",
        "Qual das seguintes atividades você teria maior interesse em realizar no seu dia a dia profissional?",
        (
            Opcao("logica", "A", "Desenvolver algoritmos, APIs e regras de negócio."),
            Opcao("interfaces", "B", "Criar interfaces visuais e melhorar a experiência dos usuários."),
            Opcao("analise", "C", "Analisar dados, identificar padrões e desenvolver modelos de inteligência artificial."),
            Opcao("engenharia_dados", "D", "Organizar grandes volumes de dados e construir pipelines de processamento."),
            Opcao("seguranca", "E", "Identificar vulnerabilidades e proteger sistemas contra ataques."),
            Opcao("devops", "F", "Automatizar processos de desenvolvimento, testes e implantação de sistemas."),
            Opcao("cloud", "G", "Projetar e administrar infraestruturas em nuvem."),
            Opcao("mobile", "H", "Desenvolver aplicativos para dispositivos móveis."),
            Opcao("qa", "I", "Testar aplicações, identificar falhas e garantir a qualidade do software."),
            Opcao("produto", "J", "Planejar produtos digitais, definir prioridades e coordenar necessidades de negócio."),
        ),
    ),
    Pergunta(
        3,
        "ferramenta",
        "Com qual das seguintes linguagens, tecnologias ou ferramentas você possui maior afinidade ou interesse em trabalhar?",
        (
            Opcao("python", "A. Python", "Automação, análise de dados e inteligência artificial."),
            Opcao("javascript", "B. JavaScript / TypeScript", "Desenvolvimento de aplicações web e interfaces."),
            Opcao("java", "C. Java / C#", "Sistemas corporativos, APIs e lógica de programação."),
            Opcao("sql", "D. SQL / Bancos de Dados", "Consultas, organização e processamento de dados."),
            Opcao("redes", "E. Linux / Redes", "Administração de sistemas, redes e segurança."),
            Opcao("devops", "F. Docker / Kubernetes / CI/CD", "Automação e implantação de aplicações."),
            Opcao("cloud", "G. AWS / Azure / Google Cloud", "Serviços e infraestrutura em nuvem."),
            Opcao("mobile", "H. Flutter / React Native / Kotlin / Swift", "Desenvolvimento de aplicativos móveis."),
            Opcao("qa", "I. Playwright / Selenium / Cypress", "Testes automatizados e qualidade de software."),
            Opcao("gestao", "J. Jira / Trello / Figma", "Gestão, planejamento e design de produtos."),
            Opcao("nenhuma", "K. Nenhuma / Iniciante", "Ainda não tenho experiência ou preferência por uma tecnologia específica."),
        ),
    ),
    Pergunta(
        4,
        "entrega",
        "Qual tipo de resultado você gostaria de proporcionar por meio do seu trabalho na área de Tecnologia da Informação?",
        (
            Opcao("funcionalidade", "A", "Desenvolver sistemas funcionais que resolvam problemas reais dos usuários e empresas."),
            Opcao("experiencia", "B", "Criar experiências digitais intuitivas, acessíveis e visualmente agradáveis."),
            Opcao("inteligencia", "C", "Transformar dados em informações, previsões e decisões inteligentes."),
            Opcao("dados", "D", "Garantir que grandes volumes de dados sejam organizados, integrados e disponibilizados corretamente."),
            Opcao("seguranca", "E", "Proteger informações, sistemas e usuários contra ameaças digitais."),
            Opcao("automacao", "F", "Tornar processos tecnológicos mais rápidos, automatizados e confiáveis."),
            Opcao("infraestrutura", "G", "Construir infraestruturas tecnológicas escaláveis, estáveis e disponíveis."),
            Opcao("mobile", "H", "Criar aplicativos móveis que facilitem atividades do cotidiano."),
            Opcao("qualidade", "I", "Garantir que sistemas funcionem corretamente, prevenindo defeitos e melhorando sua qualidade."),
            Opcao("negocios", "J", "Desenvolver estratégias e definir prioridades para produtos digitais que atendam às necessidades dos usuários e das empresas."),
        ),
    ),
)


# ---------------------------------------------------------------------------
# 2. MATRIZ DE DECISAO - DEZ TRILHAS DE CARREIRA APROVADAS
# ---------------------------------------------------------------------------
TRILHAS: tuple[Trilha, ...] = (
    Trilha(
        "backend", "Desenvolvimento Back-end",
        "Lógica de servidores, APIs, regras de negócio e bancos de dados.",
        {"media": 1, "alta": 1}, "logica", ("java",), ("python", "sql"), "funcionalidade",
    ),
    Trilha(
        "frontend_uiux", "Desenvolvimento Front-end & UI/UX",
        "Interfaces web responsivas, experiência do usuário e frameworks reativos.",
        {}, "interfaces", ("javascript",), ("gestao",), "experiencia",
    ),
    Trilha(
        "ciencia_dados_ml", "Ciência de Dados e Machine Learning",
        "Estatística, modelagem preditiva, grandes massas de dados e inteligência artificial.",
        {"media": 1, "alta": 2}, "analise", ("python",), ("sql",), "inteligencia",
    ),
    Trilha(
        "engenharia_dados", "Engenharia de Dados",
        "Arquitetura de dados, pipelines ETL/ELT e infraestrutura para Data Lakes.",
        {"media": 1, "alta": 1}, "engenharia_dados", ("sql",), ("python", "devops"), "dados",
    ),
    Trilha(
        "ciberseguranca", "Cibersegurança (Security / Pentesting)",
        "Defesa cibernética, vulnerabilidades, criptografia e redes seguras.",
        {"media": 1, "alta": 1}, "seguranca", ("redes",), ("python",), "seguranca",
    ),
    Trilha(
        "devops_sre", "DevOps & SRE",
        "Automação, integração e entrega contínua (CI/CD), contêineres e confiabilidade.",
        {"media": 1, "alta": 1}, "devops", ("devops",), ("redes", "cloud"), "automacao",
    ),
    Trilha(
        "cloud_architecture", "Computação em Nuvem (Cloud Architecture)",
        "Planejamento, migração e gestao de infraestrutura escalável na nuvem.",
        {"media": 1, "alta": 1}, "cloud", ("cloud",), ("redes", "devops"), "infraestrutura",
    ),
    Trilha(
        "desenvolvimento_mobile", "Desenvolvimento Mobile",
        "Aplicativos móveis nativos ou multiplataforma (Flutter/React Native).",
        {}, "mobile", ("mobile",), ("javascript",), "mobile",
    ),
    Trilha(
        "engenharia_qa", "Engenharia de Qualidade e Testes (QA)",
        "Testes automatizados, confiabilidade de software e processos de qualidade.",
        {}, "qa", ("qa",), ("python", "javascript"), "qualidade",
    ),
    Trilha(
        "gestao_produtos", "Gestão de Produtos (Product Management)",
        "Ponte entre negócio, design e desenvolvimento, métodos ágeis e priorização.",
        {}, "produto", ("gestao",), (), "negocios",
    ),
)


# ---------------------------------------------------------------------------
# 3. REGRAS DECLARATIVAS - TRES POR TRILHA (TOTAL: 30)
#
# Todas as dimensões informadas em cada regra formam uma conjunção (E).
# Quando uma dimensão possui uma tupla de valores, basta um deles (OU).
# As regras correspondentes são executadas pelo motor Experta.
# ---------------------------------------------------------------------------
REGRAS: tuple[Regra, ...] = (
    # Desenvolvimento Back-end: regras 1 a 3.
    _regra(1, "backend", "favoravel", "Interesse em algoritmos/APIs e afinidade com Java/C#.",
           atuacao="logica", ferramenta="java"),
    _regra(2, "backend", "favoravel", "Interesse em algoritmos/APIs e em sistemas funcionais.",
           atuacao="logica", entrega="funcionalidade"),
    _regra(3, "backend", "complementar", "Afinidade lógica, SQL e entrega de sistemas funcionais.",
           matematica=("media", "alta"), ferramenta="sql", entrega="funcionalidade"),

    # Front-end & UI/UX: regras 4 a 6.
    _regra(4, "frontend_uiux", "favoravel", "Interesse em interfaces e JavaScript/TypeScript.",
           atuacao="interfaces", ferramenta="javascript"),
    _regra(5, "frontend_uiux", "favoravel", "Interesse em interfaces e experiências acessíveis.",
           atuacao="interfaces", entrega="experiencia"),
    _regra(6, "frontend_uiux", "complementar", "Afinidade com o grupo Jira/Trello/Figma e com experiências visuais.",
           ferramenta="gestao", entrega="experiencia"),

    # Ciência de Dados e Machine Learning: regras 7 a 9.
    _regra(7, "ciencia_dados_ml", "favoravel", "Alta afinidade matemática e interesse em modelos de IA.",
           matematica="alta", atuacao="analise"),
    _regra(8, "ciencia_dados_ml", "favoravel", "Interesse em análise de dados e previsões.",
           atuacao="analise", entrega="inteligencia"),
    _regra(9, "ciencia_dados_ml", "complementar", "Python, afinidade matemática e interesse em previsões.",
           ferramenta="python", matematica=("media", "alta"), entrega="inteligencia"),

    # Engenharia de Dados: regras 10 a 12.
    _regra(10, "engenharia_dados", "favoravel", "Interesse em pipelines e SQL/Bancos de Dados.",
           atuacao="engenharia_dados", ferramenta="sql"),
    _regra(11, "engenharia_dados", "favoravel", "Interesse em pipelines e integração/disponibilidade de dados.",
           atuacao="engenharia_dados", entrega="dados"),
    _regra(12, "engenharia_dados", "complementar", "Matemática, Python ou Docker/CI-CD e integração de dados.",
           matematica=("media", "alta"), ferramenta=("python", "devops"), entrega="dados"),

    # Cibersegurança: regras 13 a 15.
    _regra(13, "ciberseguranca", "favoravel", "Interesse em vulnerabilidades e Linux/Redes.",
           atuacao="seguranca", ferramenta="redes"),
    _regra(14, "ciberseguranca", "favoravel", "Interesse em vulnerabilidades e proteção de sistemas.",
           atuacao="seguranca", entrega="seguranca"),
    _regra(15, "ciberseguranca", "complementar", "Linux/Redes ou Python, matemática e proteção digital.",
           ferramenta=("redes", "python"), matematica=("media", "alta"), entrega="seguranca"),

    # DevOps & SRE: regras 16 a 18.
    _regra(16, "devops_sre", "favoravel", "Interesse em automação de implantação e Docker/Kubernetes/CI-CD.",
           atuacao="devops", ferramenta="devops"),
    _regra(17, "devops_sre", "favoravel", "Interesse em automação e confiabilidade operacional.",
           atuacao="devops", entrega="automacao"),
    _regra(18, "devops_sre", "complementar", "Docker/Kubernetes/CI-CD e melhoria de processos.",
           ferramenta="devops", entrega="automacao"),

    # Computação em Nuvem: regras 19 a 21.
    _regra(19, "cloud_architecture", "favoravel", "Interesse em infraestrutura de nuvem e AWS/Azure/GCP.",
           atuacao="cloud", ferramenta="cloud"),
    _regra(20, "cloud_architecture", "favoravel", "Interesse em arquitetura de nuvem e escalabilidade.",
           atuacao="cloud", entrega="infraestrutura"),
    _regra(21, "cloud_architecture", "complementar", "Linux/Redes ou Docker/CI-CD, matemática e escalabilidade.",
           ferramenta=("redes", "devops"), matematica=("media", "alta"), entrega="infraestrutura"),

    # Desenvolvimento Mobile: regras 22 a 24.
    _regra(22, "desenvolvimento_mobile", "favoravel", "Interesse em aplicativos móveis e Flutter/React Native/Kotlin/Swift.",
           atuacao="mobile", ferramenta="mobile"),
    _regra(23, "desenvolvimento_mobile", "favoravel", "Interesse em aplicativos móveis e soluções para o cotidiano.",
           atuacao="mobile", entrega="mobile"),
    _regra(24, "desenvolvimento_mobile", "complementar", "JavaScript/TypeScript ou tecnologias mobile para aplicativos.",
           ferramenta=("javascript", "mobile"), entrega="mobile"),

    # Engenharia de Qualidade e Testes: regras 25 a 27.
    _regra(25, "engenharia_qa", "favoravel", "Interesse em testar sistemas e Playwright/Selenium/Cypress.",
           atuacao="qa", ferramenta="qa"),
    _regra(26, "engenharia_qa", "favoravel", "Interesse em testar aplicações e prevenir defeitos.",
           atuacao="qa", entrega="qualidade"),
    _regra(27, "engenharia_qa", "complementar", "Python/JavaScript/ferramentas QA e garantia de qualidade.",
           ferramenta=("python", "javascript", "qa"), entrega="qualidade"),

    # Gestão de Produtos: regras 28 a 30.
    _regra(28, "gestao_produtos", "favoravel", "Interesse em planejar produtos e Jira/Trello/Figma.",
           atuacao="produto", ferramenta="gestao"),
    _regra(29, "gestao_produtos", "favoravel", "Interesse em planejar produtos e estrategia de negócio.",
           atuacao="produto", entrega="negocios"),
    _regra(30, "gestao_produtos", "complementar", "Jira/Trello/Figma e priorização de produtos digitais.",
           ferramenta="gestao", entrega="negocios"),
)


# ---------------------------------------------------------------------------
# 4. POLITICA DE PONTUACAO E DESEMPATE APROVADA
# ---------------------------------------------------------------------------
PESOS_PONTUACAO: dict[str, int] = {
    "atuacao_correspondente": 5,
    "ferramenta_principal": 3,
    "ferramenta_complementar": 1,
    "entrega_correspondente": 5,
}

# O critério matematico já tem pontuação especificada em cada Trilha:
# - Em Ciência de Dados, media = 1 e alta = 2;
# - Em Back-end, Engenharia de Dados, Cibersegurança, DevOps e Cloud,
#   media = 1 e alta = 1;
# - Nas demais carreiras, nenhuma afinidade matemática acrescenta pontos.
# A resposta baixa nunca elimina uma carreira. 'nenhuma' (ferramenta) vale 0.
# Cada dimensão contribui no máximo uma vez por carreira. Os disparos das
# regras contribuem somente para desempatar carreiras de mesma pontuação,
# sem acrescentar pontos nem duplicar critérios individuais.

ORDEM_DESEMPATE: tuple[str, ...] = (
    "atuacao",               # 1o: atividade profissional escolhida (pergunta 2)
    "entrega",               # 2o: resultado desejado (pergunta 4)
    "ferramenta_principal",  # 3o: afinidade com ferramenta principal (pergunta 3)
    "matematica",            # 4o: compatibilidade matemática (pergunta 1)
)


# ---------------------------------------------------------------------------
# 5. VERIFICACAO ESTRUTURAL DA BASE - NAO E UM MOTOR DE INFERENCIA
# ---------------------------------------------------------------------------
def validar_base_conhecimento() -> None:
    """Verifica integridade, contagens e referências dos dados declarados.

    Nao entrevista usuários, não calcula pontuacoes e não dispara regras.
    Lanca ValueError se algum cadastro estiver inconsistente.
    """

    if len(PERGUNTAS) != 4 or [p.numero for p in PERGUNTAS] != [1, 2, 3, 4]:
        raise ValueError("A entrevista deve conter exatamente as quatro perguntas aprovadas.")

    dimensoes = {p.dimensao for p in PERGUNTAS}
    if dimensoes != {"matematica", "atuacao", "ferramenta", "entrega"}:
        raise ValueError("As quatro dimensões da entrevista estão incorretas.")

    opcoes = {}
    for pergunta in PERGUNTAS:
        codigos = [opcao.codigo for opcao in pergunta.opcoes]
        if len(codigos) != len(set(codigos)) or not codigos:
            raise ValueError(f"Opcoes duplicadas ou ausentes na pergunta {pergunta.numero}.")
        opcoes[pergunta.dimensao] = set(codigos)

    if [len(p.opcoes) for p in PERGUNTAS] != [3, 10, 11, 10]:
        raise ValueError("Quantidade de alternativas diferente da aprovada.")

    codigos_trilhas = [trilha.codigo for trilha in TRILHAS]
    if len(TRILHAS) != 10 or len(set(codigos_trilhas)) != 10:
        raise ValueError("A base deve possuir dez trilhas com códigos únicos.")

    for trilha in TRILHAS:
        if not set(trilha.matematica).issubset(opcoes["matematica"]):
            raise ValueError(f"Matematica invalida em {trilha.codigo}.")
        if any(pontos not in (1, 2) for pontos in trilha.matematica.values()):
            raise ValueError(f"Pontuacao matematica invalida em {trilha.codigo}.")
        if trilha.atuacao not in opcoes["atuacao"] or trilha.entrega not in opcoes["entrega"]:
            raise ValueError(f"Atuacao ou entrega invalida em {trilha.codigo}.")
        principais = set(trilha.ferramentas_principais)
        complementares = set(trilha.ferramentas_complementares)
        if not principais or principais & complementares:
            raise ValueError(f"Ferramentas principais/complementares invalidas em {trilha.codigo}.")
        if not (principais | complementares).issubset(opcoes["ferramenta"]):
            raise ValueError(f"Ferramenta nao cadastrada em {trilha.codigo}.")
        if "nenhuma" in principais | complementares:
            raise ValueError("A opção Nenhuma/Iniciante não pode pontuar.")

    if len(REGRAS) != 30 or sorted(regra.numero for regra in REGRAS) != list(range(1, 31)):
        raise ValueError("As regras devem ter números únicos de 1 a 30.")

    contagem = Counter(regra.trilha for regra in REGRAS)
    if set(contagem) != set(codigos_trilhas) or any(valor != 3 for valor in contagem.values()):
        raise ValueError("Cada uma das dez trilhas deve possuir três regras.")

    for regra in REGRAS:
        if regra.tipo not in {"favoravel", "complementar"} or not regra.condicoes:
            raise ValueError(f"Tipo/condicoes invalidos na regra {regra.numero}.")
        nomes_dimensoes = [condicao.dimensao for condicao in regra.condicoes]
        if len(nomes_dimensoes) != len(set(nomes_dimensoes)):
            raise ValueError(f"Dimensao repetida na regra {regra.numero}.")
        for condicao in regra.condicoes:
            if condicao.dimensao not in opcoes or not condicao.valores:
                raise ValueError(f"Dimensao/valores ausentes na regra {regra.numero}.")
            if not set(condicao.valores).issubset(opcoes[condicao.dimensao]):
                raise ValueError(f"Alternativa nao cadastrada na regra {regra.numero}.")

    if ORDEM_DESEMPATE != ("atuacao", "entrega", "ferramenta_principal", "matematica"):
        raise ValueError("A ordem de desempate difere da aprovada.")
    if PESOS_PONTUACAO != {
        "atuacao_correspondente": 5,
        "ferramenta_principal": 3,
        "ferramenta_complementar": 1,
        "entrega_correspondente": 5,
    }:
        raise ValueError("Os pesos de pontuação diferem dos aprovados.")


if __name__ == "__main__":
    validar_base_conhecimento()
    print("Base de conhecimento validada com sucesso!")
    print(f"Perguntas: {len(PERGUNTAS)}")
    print(f"Trilhas de carreira: {len(TRILHAS)}")
    print(f"Regras declarativas: {len(REGRAS)}")
    print("Pontuação e desempate: configurados")
    print("Base de conhecimento verificada e pronta para uso no motor.")
