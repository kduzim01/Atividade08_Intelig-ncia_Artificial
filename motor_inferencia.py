"""Motor de inferência do Consultor Inteligente de Carreiras em TI.

Atividade Aula 08 — Fase 2, etapa 2.90.

Preserva as trinta regras Experta e seus cenários de teste. Calcula a
pontuação de cada trilha a partir das quatro respostas e dos pesos da
Fase 1, sem duplicar pontos por quantidade de regras disparadas.
Aplica os quatro critérios de desempate aprovados, apenas às trilhas
empatadas na maior pontuação. Produz uma recomendação justificada,
separando as regras realmente disparadas das evidências individuais
de pontuação e indicando os empates resolvidos.
"""

from __future__ import annotations

import collections
import collections.abc
from dataclasses import dataclass

# Compatibilidade temporária do frozendict 1.2 (Experta 1.9.4) com Python 3.12.
# O ajuste ocorre apenas neste processo; não modifica bibliotecas instaladas.
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

from experta import OR, Fact, KnowledgeEngine, Rule

from base_conhecimento import (
    PERGUNTAS,
    ORDEM_DESEMPATE,
    PESOS_PONTUACAO,
    REGRAS,
    TRILHAS,
    Regra,
    validar_base_conhecimento,
)


@dataclass(frozen=True)
class PontuacaoTrilha:
    """Detalhamento dos pontos de uma trilha, sem multiplicar critérios.

    Os campos de ferramenta são mutuamente exclusivos: a mesma alternativa
    não pode valer como principal e complementar para a mesma carreira.
    """

    codigo_trilha: str
    nome_trilha: str
    matematica: int
    atuacao: int
    ferramenta_principal: int
    ferramenta_complementar: int
    entrega: int

    @property
    def total(self) -> int:
        return (
            self.matematica
            + self.atuacao
            + self.ferramenta_principal
            + self.ferramenta_complementar
            + self.entrega
        )


@dataclass(frozen=True)
class ResultadoDesempate:
    """Desempate entre as carreiras com a mesma maior pontuação.

    Identifica qual critério aprovado separou os candidatos. Não gera,
    por si só, uma recomendação ao usuário nem constrói justificativas.
    """

    candidatos_originais: tuple[str, ...]
    codigo_selecionado: str
    pontuacao_empatada: int
    criterio_decisivo: str


@dataclass(frozen=True)
class ResultadoRecomendacao:
    """Decisão fundamentada e auditável, pronta para a futura interface web.

    ``regras_da_trilha`` lista apenas regras Experta REALMENTE disparadas
    para a carreira selecionada. ``regras_de_outras_trilhas`` informa
    disparos das demais carreiras para total transparência.
    As justificativas de pontuação são distintas das regras cruzadas.
    """

    codigo_trilha: str
    nome_trilha: str
    pontuacao_total: int
    detalhamento: PontuacaoTrilha
    pontuacoes: tuple[PontuacaoTrilha, ...]
    regras_da_trilha: tuple[Regra, ...]
    regras_de_outras_trilhas: tuple[Regra, ...]
    justificativas_pontuacao: tuple[str, ...]
    desempate: ResultadoDesempate | None

    def formatar(self) -> str:
        """Formata a recomendação em texto, sem dependência do Streamlit."""
        linhas = [
            f"Carreira recomendada: {self.nome_trilha}",
            f"Pontuação final: {self.pontuacao_total} pontos",
            "Critérios de pontuação utilizados:",
        ]
        linhas.extend(f"  - {motivo}" for motivo in self.justificativas_pontuacao)
        linhas.append("Regras cruzadas disparadas para a carreira recomendada:")
        if self.regras_da_trilha:
            linhas.extend(
                f"  - Regra {regra.numero}: {regra.motivo}"
                for regra in self.regras_da_trilha
            )
        else:
            linhas.append(
                "  - Nenhuma regra cruzada dessa carreira foi disparada. "
                "A escolha decorreu dos critérios individuais de pontuação "
                "e, quando necessário, do desempate."
            )
        if self.desempate is not None:
            candidatos = ", ".join(
                next(trilha.nome for trilha in TRILHAS if trilha.codigo == codigo)
                for codigo in self.desempate.candidatos_originais
            )
            nomes = {
                "atuacao": "preferência de atuação diária",
                "entrega": "tipo de entrega de valor",
                "ferramenta_principal": "afinidade com ferramenta principal",
                "matematica": "afinidade matemática",
            }
            linhas.append(
                f"Desempate: {candidatos} empataram com "
                f"{self.desempate.pontuacao_empatada} pontos. "
                f"O critério decisivo foi {nomes[self.desempate.criterio_decisivo]}."
            )
        if self.regras_de_outras_trilhas:
            linhas.append("Outras regras cruzadas também disparadas (não decisivas):")
            linhas.extend(
                f"  - Regra {regra.numero}: {regra.motivo}"
                for regra in self.regras_de_outras_trilhas
            )
        return "\n".join(linhas)


class PerfilUsuario(Fact):
    """Fato com as quatro respostas da entrevista, usando os códigos da Fase 1."""


class MotorInferencia(KnowledgeEngine):
    """Executa as 30 regras e calcula a pontuação independente dos disparos."""

    def __init__(self) -> None:
        super().__init__()
        self.regras_disparadas: list[Regra] = []
        self._respostas_atuais: dict[str, str] | None = None

    def registrar_perfil(self, respostas: dict[str, str]) -> None:
        """Valida respostas e declara exatamente um fato PerfilUsuario.

        As chaves devem ser: matematica, atuacao, ferramenta e entrega.
        Os valores devem corresponder aos códigos cadastrados em PERGUNTAS.
        """
        validar_base_conhecimento()

        alternativas = {
            pergunta.dimensao: {opcao.codigo for opcao in pergunta.opcoes}
            for pergunta in PERGUNTAS
        }

        if set(respostas) != set(alternativas):
            faltantes = sorted(set(alternativas) - set(respostas))
            extras = sorted(set(respostas) - set(alternativas))
            raise ValueError(
                f"Dimensões inválidas. Faltantes: {faltantes}; extras: {extras}."
            )

        for dimensao, valor in respostas.items():
            if valor not in alternativas[dimensao]:
                raise ValueError(
                    f"Resposta inválida para '{dimensao}': {valor!r}."
                )

        # Cada entrevista começa com fatos e disparos novos.
        self.reset()
        self.regras_disparadas.clear()
        self.declare(PerfilUsuario(**respostas))
        self._respostas_atuais = dict(respostas)

    def _registrar_disparo(self, numero: int) -> None:
        """Guarda a regra aprovada na Fase 1, incluindo seu motivo original."""
        regra = next((item for item in REGRAS if item.numero == numero), None)
        trilhas_implementadas = {
            1: "backend", 2: "backend", 3: "backend",
            4: "frontend_uiux", 5: "frontend_uiux", 6: "frontend_uiux",
            7: "ciencia_dados_ml", 8: "ciencia_dados_ml", 9: "ciencia_dados_ml",
            10: "engenharia_dados", 11: "engenharia_dados", 12: "engenharia_dados",
            13: "ciberseguranca", 14: "ciberseguranca", 15: "ciberseguranca",
            16: "devops_sre", 17: "devops_sre", 18: "devops_sre",
            19: "cloud_architecture", 20: "cloud_architecture", 21: "cloud_architecture",
            22: "desenvolvimento_mobile", 23: "desenvolvimento_mobile", 24: "desenvolvimento_mobile",
            25: "engenharia_qa", 26: "engenharia_qa", 27: "engenharia_qa",
            28: "gestao_produtos", 29: "gestao_produtos", 30: "gestao_produtos",
        }
        if regra is None or regra.trilha != trilhas_implementadas.get(numero):
            raise ValueError(f"Regra de inferência não encontrada: {numero}.")
        if regra.numero not in {item.numero for item in self.regras_disparadas}:
            self.regras_disparadas.append(regra)

    def calcular_pontuacoes(self) -> tuple[PontuacaoTrilha, ...]:
        """Aplica a matriz de pesos da Fase 1 às quatro respostas do perfil.

        O resultado contém as dez carreiras na ordem da base declarativa.
        Cada pergunta contribui no máximo uma vez para cada trilha;
        regras disparadas servem para registrar evidências, não para
        multiplicar pontos. Não decide a carreira vencedora nem desempata.
        """
        if self._respostas_atuais is None:
            raise RuntimeError("Registre um perfil antes de calcular pontuações.")

        respostas = self._respostas_atuais
        pontuacoes: list[PontuacaoTrilha] = []
        for trilha in TRILHAS:
            ferramenta = respostas["ferramenta"]
            principal = (
                PESOS_PONTUACAO["ferramenta_principal"]
                if ferramenta in trilha.ferramentas_principais else 0
            )
            complementar = (
                PESOS_PONTUACAO["ferramenta_complementar"]
                if ferramenta in trilha.ferramentas_complementares else 0
            )
            pontuacoes.append(
                PontuacaoTrilha(
                    codigo_trilha=trilha.codigo,
                    nome_trilha=trilha.nome,
                    matematica=trilha.matematica.get(respostas["matematica"], 0),
                    atuacao=(
                        PESOS_PONTUACAO["atuacao_correspondente"]
                        if respostas["atuacao"] == trilha.atuacao else 0
                    ),
                    ferramenta_principal=principal,
                    ferramenta_complementar=complementar,
                    entrega=(
                        PESOS_PONTUACAO["entrega_correspondente"]
                        if respostas["entrega"] == trilha.entrega else 0
                    ),
                )
            )
        return tuple(pontuacoes)

    def resolver_desempate(self) -> ResultadoDesempate | None:
        """Desempata apenas as carreiras com a maior pontuação total.

        Retorna ``None`` se houver um único primeiro colocado, pois nesse
        caso não há empate a resolver. Não produz recomendação final.
        """
        return self._desempatar_pontuacoes(self.calcular_pontuacoes())

    @staticmethod
    def _desempatar_pontuacoes(
        pontuacoes: tuple[PontuacaoTrilha, ...],
    ) -> ResultadoDesempate | None:
        """Aplica a ORDEM_DESEMPATE, sem alterar pontos ou regras disparadas.

        O método separado permite testar cada prioridade mesmo quando os
        perfis reais normalmente desempatem já pela preferência de atuação.
        """
        if not pontuacoes:
            raise ValueError("A lista de pontuações não pode estar vazia.")

        maior_total = max(item.total for item in pontuacoes)
        empatadas = [item for item in pontuacoes if item.total == maior_total]
        if len(empatadas) == 1:
            return None

        candidatos_originais = tuple(item.codigo_trilha for item in empatadas)
        for criterio in ORDEM_DESEMPATE:
            maior_criterio = max(getattr(item, criterio) for item in empatadas)
            empatadas = [
                item for item in empatadas
                if getattr(item, criterio) == maior_criterio
            ]
            if len(empatadas) == 1:
                return ResultadoDesempate(
                    candidatos_originais=candidatos_originais,
                    codigo_selecionado=empatadas[0].codigo_trilha,
                    pontuacao_empatada=maior_total,
                    criterio_decisivo=criterio,
                )

        # Não introduz uma quinta prioridade ou a ordem de cadastro como
        # desempate implícito. Caso impossível nos perfis atuais da Fase 1.
        raise RuntimeError(
            "Empate persistente após todos os critérios aprovados: "
            + ", ".join(item.codigo_trilha for item in empatadas)
        )

    def recomendar_carreira(self) -> ResultadoRecomendacao:
        """Gera uma recomendação e explicita as evidências efetivamente usadas.

        Executa o motor Experta para registrar disparos antes de coletar
        justificativas. A pontuação segue a matriz de pesos da Fase 1,
        não a quantidade de regras. A seleção respeita o desempate aprovado.
        """
        if self._respostas_atuais is None:
            raise RuntimeError("Registre um perfil antes de recomendar uma carreira.")

        # Caso o chamador ainda não tenha chamado run(), faz isso agora.
        # O Experta mantém as ativações consumidas até registrar outro perfil.
        self.run()
        pontuacoes = self.calcular_pontuacoes()
        maior = max(p.total for p in pontuacoes)
        primeiras = [p for p in pontuacoes if p.total == maior]
        desempate = self._desempatar_pontuacoes(pontuacoes)
        codigo_vencedor = (
            primeiras[0].codigo_trilha
            if desempate is None else desempate.codigo_selecionado
        )
        selecionada = next(
            p for p in pontuacoes if p.codigo_trilha == codigo_vencedor
        )
        regras_disparadas = sorted(self.regras_disparadas, key=lambda r: r.numero)
        regras_da_trilha = tuple(
            r for r in regras_disparadas if r.trilha == codigo_vencedor
        )
        outras_regras = tuple(
            r for r in regras_disparadas if r.trilha != codigo_vencedor
        )
        justificativas = self._justificar_pontuacao(selecionada)

        return ResultadoRecomendacao(
            codigo_trilha=codigo_vencedor,
            nome_trilha=selecionada.nome_trilha,
            pontuacao_total=selecionada.total,
            detalhamento=selecionada,
            pontuacoes=pontuacoes,
            regras_da_trilha=regras_da_trilha,
            regras_de_outras_trilhas=outras_regras,
            justificativas_pontuacao=justificativas,
            desempate=desempate,
        )

    def _justificar_pontuacao(
        self, pontos: PontuacaoTrilha
    ) -> tuple[str, ...]:
        """Fundamenta cada parcela da pontuação usando as opções aprovadas."""
        assert self._respostas_atuais is not None
        respostas = self._respostas_atuais
        alternativas = {
            pergunta.dimensao: {opcao.codigo: opcao for opcao in pergunta.opcoes}
            for pergunta in PERGUNTAS
        }
        mat = alternativas["matematica"][respostas["matematica"]]
        atuacao = alternativas["atuacao"][respostas["atuacao"]]
        ferramenta = alternativas["ferramenta"][respostas["ferramenta"]]
        entrega = alternativas["entrega"][respostas["entrega"]]

        justificativas = [
            f"Afinidade matemática ({mat.titulo}): +{pontos.matematica} "
            "(não é critério eliminatório).",
        ]
        if pontos.atuacao:
            justificativas.append(
                f"Atuação profissional: {atuacao.descricao} "
                f"(+{pontos.atuacao})."
            )
        if pontos.ferramenta_principal:
            justificativas.append(
                f"Ferramenta principal: {ferramenta.titulo} "
                f"(+{pontos.ferramenta_principal})."
            )
        elif pontos.ferramenta_complementar:
            justificativas.append(
                f"Ferramenta complementar: {ferramenta.titulo} "
                f"(+{pontos.ferramenta_complementar})."
            )
        if pontos.entrega:
            justificativas.append(
                f"Entrega de valor: {entrega.descricao} "
                f"(+{pontos.entrega})."
            )
        return tuple(justificativas)

    # Regra 1: atuação em algoritmos/APIs E afinidade com Java/C#.
    @Rule(PerfilUsuario(atuacao="logica", ferramenta="java"))
    def regra_01_backend(self) -> None:
        self._registrar_disparo(1)

    # Regra 2: atuação em algoritmos/APIs E entrega de sistemas funcionais.
    @Rule(PerfilUsuario(atuacao="logica", entrega="funcionalidade"))
    def regra_02_backend(self) -> None:
        self._registrar_disparo(2)

    # Regra 3: matemática Média OU Alta, E SQL, E entrega funcional.
    @Rule(
        OR(
            PerfilUsuario(matematica="media", ferramenta="sql", entrega="funcionalidade"),
            PerfilUsuario(matematica="alta", ferramenta="sql", entrega="funcionalidade"),
        )
    )
    def regra_03_backend(self) -> None:
        self._registrar_disparo(3)


    # Regra 4: atuação em interfaces E afinidade com JavaScript/TypeScript.
    @Rule(PerfilUsuario(atuacao="interfaces", ferramenta="javascript"))
    def regra_04_frontend_uiux(self) -> None:
        self._registrar_disparo(4)

    # Regra 5: atuação em interfaces E entrega de experiências acessíveis.
    @Rule(PerfilUsuario(atuacao="interfaces", entrega="experiencia"))
    def regra_05_frontend_uiux(self) -> None:
        self._registrar_disparo(5)

    # Regra 6: grupo Jira/Trello/Figma E entrega de experiências visuais.
    @Rule(PerfilUsuario(ferramenta="gestao", entrega="experiencia"))
    def regra_06_frontend_uiux(self) -> None:
        self._registrar_disparo(6)

    # Regra 7: matemática Alta E atuação em análise/modelos de IA.
    @Rule(PerfilUsuario(matematica="alta", atuacao="analise"))
    def regra_07_ciencia_dados_ml(self) -> None:
        self._registrar_disparo(7)

    # Regra 8: atuação em análise E entrega de previsões inteligentes.
    @Rule(PerfilUsuario(atuacao="analise", entrega="inteligencia"))
    def regra_08_ciencia_dados_ml(self) -> None:
        self._registrar_disparo(8)

    # Regra 9: Python E matemática Média OU Alta E entrega inteligente.
    @Rule(
        OR(
            PerfilUsuario(matematica="media", ferramenta="python", entrega="inteligencia"),
            PerfilUsuario(matematica="alta", ferramenta="python", entrega="inteligencia"),
        )
    )
    def regra_09_ciencia_dados_ml(self) -> None:
        self._registrar_disparo(9)


    # Regra 10: atuação em pipelines/Engenharia de Dados E ferramenta SQL.
    @Rule(PerfilUsuario(atuacao="engenharia_dados", ferramenta="sql"))
    def regra_10_engenharia_dados(self) -> None:
        self._registrar_disparo(10)

    # Regra 11: atuação em pipelines E entrega de dados integrados/disponíveis.
    @Rule(PerfilUsuario(atuacao="engenharia_dados", entrega="dados"))
    def regra_11_engenharia_dados(self) -> None:
        self._registrar_disparo(11)

    # Regra 12: matemática Média OU Alta E Python OU Docker/CI-CD E entrega de dados.
    @Rule(
        OR(
            PerfilUsuario(matematica="media", ferramenta="python", entrega="dados"),
            PerfilUsuario(matematica="alta", ferramenta="python", entrega="dados"),
            PerfilUsuario(matematica="media", ferramenta="devops", entrega="dados"),
            PerfilUsuario(matematica="alta", ferramenta="devops", entrega="dados"),
        )
    )
    def regra_12_engenharia_dados(self) -> None:
        self._registrar_disparo(12)

    # Regra 13: atuação em vulnerabilidades/proteção E afinidade com Linux/Redes.
    @Rule(PerfilUsuario(atuacao="seguranca", ferramenta="redes"))
    def regra_13_ciberseguranca(self) -> None:
        self._registrar_disparo(13)

    # Regra 14: atuação em vulnerabilidades E entrega de proteção de sistemas.
    @Rule(PerfilUsuario(atuacao="seguranca", entrega="seguranca"))
    def regra_14_ciberseguranca(self) -> None:
        self._registrar_disparo(14)

    # Regra 15: Linux/Redes OU Python, matemática Média OU Alta e entrega de proteção.
    @Rule(
        OR(
            PerfilUsuario(matematica="media", ferramenta="redes", entrega="seguranca"),
            PerfilUsuario(matematica="alta", ferramenta="redes", entrega="seguranca"),
            PerfilUsuario(matematica="media", ferramenta="python", entrega="seguranca"),
            PerfilUsuario(matematica="alta", ferramenta="python", entrega="seguranca"),
        )
    )
    def regra_15_ciberseguranca(self) -> None:
        self._registrar_disparo(15)

    # Regra 16: atuação em automação/implantação E Docker/Kubernetes/CI-CD.
    @Rule(PerfilUsuario(atuacao="devops", ferramenta="devops"))
    def regra_16_devops_sre(self) -> None:
        self._registrar_disparo(16)

    # Regra 17: atuação em automação E entrega de processos automatizados/confiáveis.
    @Rule(PerfilUsuario(atuacao="devops", entrega="automacao"))
    def regra_17_devops_sre(self) -> None:
        self._registrar_disparo(17)

    # Regra 18: Docker/Kubernetes/CI-CD E entrega de automação/confiabilidade.
    @Rule(PerfilUsuario(ferramenta="devops", entrega="automacao"))
    def regra_18_devops_sre(self) -> None:
        self._registrar_disparo(18)


    # Regra 19: interesse em infraestrutura de nuvem E afinidade com AWS/Azure/GCP.
    @Rule(PerfilUsuario(atuacao="cloud", ferramenta="cloud"))
    def regra_19_cloud_architecture(self) -> None:
        self._registrar_disparo(19)

    # Regra 20: atuação em arquitetura de nuvem E entrega de infraestrutura escalável.
    @Rule(PerfilUsuario(atuacao="cloud", entrega="infraestrutura"))
    def regra_20_cloud_architecture(self) -> None:
        self._registrar_disparo(20)

    # Regra 21: matemática Média OU Alta, Linux/Redes OU Docker/CI-CD,
    # e entrega de infraestrutura escalável/estável/disponível.
    @Rule(
        OR(
            PerfilUsuario(matematica="media", ferramenta="redes", entrega="infraestrutura"),
            PerfilUsuario(matematica="alta", ferramenta="redes", entrega="infraestrutura"),
            PerfilUsuario(matematica="media", ferramenta="devops", entrega="infraestrutura"),
            PerfilUsuario(matematica="alta", ferramenta="devops", entrega="infraestrutura"),
        )
    )
    def regra_21_cloud_architecture(self) -> None:
        self._registrar_disparo(21)


    # Regra 22: atuação em desenvolvimento de apps E ferramentas Mobile.
    @Rule(PerfilUsuario(atuacao="mobile", ferramenta="mobile"))
    def regra_22_desenvolvimento_mobile(self) -> None:
        self._registrar_disparo(22)

    # Regra 23: atuação em Mobile E entrega de apps para o cotidiano.
    @Rule(PerfilUsuario(atuacao="mobile", entrega="mobile"))
    def regra_23_desenvolvimento_mobile(self) -> None:
        self._registrar_disparo(23)

    # Regra 24: JavaScript/TypeScript OU tecnologias Mobile E entrega de apps.
    @Rule(
        OR(
            PerfilUsuario(ferramenta="javascript", entrega="mobile"),
            PerfilUsuario(ferramenta="mobile", entrega="mobile"),
        )
    )
    def regra_24_desenvolvimento_mobile(self) -> None:
        self._registrar_disparo(24)

    # Regra 25: atuação em testes de software E ferramenta QA.
    @Rule(PerfilUsuario(atuacao="qa", ferramenta="qa"))
    def regra_25_engenharia_qa(self) -> None:
        self._registrar_disparo(25)

    # Regra 26: atuação em testes E entrega focada em qualidade de software.
    @Rule(PerfilUsuario(atuacao="qa", entrega="qualidade"))
    def regra_26_engenharia_qa(self) -> None:
        self._registrar_disparo(26)

    # Regra 27: Python OU JavaScript/TypeScript OU ferramentas QA,
    # combinados com entrega de qualidade de software.
    @Rule(
        OR(
            PerfilUsuario(ferramenta="python", entrega="qualidade"),
            PerfilUsuario(ferramenta="javascript", entrega="qualidade"),
            PerfilUsuario(ferramenta="qa", entrega="qualidade"),
        )
    )
    def regra_27_engenharia_qa(self) -> None:
        self._registrar_disparo(27)


    # Regra 28: atuação em planejamento de produtos E Jira/Trello/Figma.
    @Rule(PerfilUsuario(atuacao="produto", ferramenta="gestao"))
    def regra_28_gestao_produtos(self) -> None:
        self._registrar_disparo(28)

    # Regra 29: atuação em produtos E entrega de estratégias de negócio.
    @Rule(PerfilUsuario(atuacao="produto", entrega="negocios"))
    def regra_29_gestao_produtos(self) -> None:
        self._registrar_disparo(29)

    # Regra 30: ferramentas Jira/Trello/Figma E entrega de negócios.
    @Rule(PerfilUsuario(ferramenta="gestao", entrega="negocios"))
    def regra_30_gestao_produtos(self) -> None:
        self._registrar_disparo(30)


if __name__ == "__main__":
    motor = MotorInferencia()

    # Preserva o teste original: perfil de QA não deve disparar regras Back-end.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "qa",
        "ferramenta": "qa", "entrega": "qualidade",
    })
    perfis = [
        fato for fato in motor.facts.values()
        if isinstance(fato, PerfilUsuario)
    ]
    assert len(perfis) == 1, "Deveria existir um único fato de perfil."
    motor.run()
    assert all(
        regra.numero not in (1, 2, 3) for regra in motor.regras_disparadas
    ), "Perfil QA não deve ativar regras Back-end."
    print("Motor inicializado e base validada com sucesso!")
    print("Fato PerfilUsuario registrado com as quatro respostas.")
    print("Perfil QA: nenhuma regra Back-end disparada (correto).")

    # Java/C# + algoritmos/APIs + sistemas funcionais: regras 1 e 2.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "logica",
        "ferramenta": "java", "entrega": "funcionalidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [1, 2], f"Esperadas as regras [1, 2]; obtidas {numeros}."
    print(f"Perfil Back-end com Java: regras disparadas {numeros}.")

    # SQL + matemática média/alta + entrega funcional: regra 3.
    for nivel in ("media", "alta"):
        motor.registrar_perfil({
            "matematica": nivel, "atuacao": "interfaces",
            "ferramenta": "sql", "entrega": "funcionalidade",
        })
        motor.run()
        numeros = sorted(regra.numero for regra in motor.regras_disparadas)
        assert numeros == [3], f"Matemática {nivel}: esperada [3], obtidas {numeros}."
        print(f"Perfil Back-end com SQL, matemática {nivel}: regras disparadas {numeros}.")

    # Afinidade matemática baixa não deve disparar a regra 3.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "interfaces",
        "ferramenta": "sql", "entrega": "funcionalidade",
    })
    motor.run()
    assert not motor.regras_disparadas, "Matemática baixa não deve disparar regra 3."
    print("Perfil com matemática baixa e SQL: nenhuma regra Back-end disparada.")
    print("Regras de Back-end 1, 2 e 3 validadas nos exemplos!")

    # JavaScript/TypeScript + interfaces + experiência: regras 4 e 5.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "interfaces",
        "ferramenta": "javascript", "entrega": "experiencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [4, 5], f"Front-end com JavaScript: esperado [4, 5], obtido {numeros}."
    print(f"Perfil Front-end com JavaScript: regras disparadas {numeros}.")

    # Ferramentas de design + experiência acionam a regra 6; atuação em produto e
    # ferramenta de gestão também acionam legitimamente a nova regra 28.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "gestao", "entrega": "experiencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [6, 28], f"Design e planejamento: esperado [6, 28], obtido {numeros}."
    print(f"Perfil com Jira/Trello/Figma e experiência: regras disparadas {numeros}.")

    # Atuação em interfaces + ferramentas de gestão/design + experiência: regras 5 e 6.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "interfaces",
        "ferramenta": "gestao", "entrega": "experiencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [5, 6], f"Interfaces e design: esperado [5, 6], obtido {numeros}."
    print(f"Perfil de interfaces com Figma: regras disparadas {numeros}.")

    # JavaScript sem atuação em interfaces não ativa Front-end;
    # atuar em Produtos + entrega de negócios passa a disparar regra 29.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "javascript", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"Sem Front-end, mas com gestão de produto: esperado [29], obtido {numeros}."
    print("Perfil com JavaScript, sem foco em interfaces: nenhuma regra Front-end; regra 29 de Produtos disparada.")
    print("Regras de Front-end & UI/UX 4, 5 e 6 validadas nos exemplos!")

    # Alta afinidade matemática + análise + Python + previsões: regras 7, 8 e 9.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "analise",
        "ferramenta": "python", "entrega": "inteligencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [7, 8, 9], f"Cientista de Dados: esperado [7, 8, 9], obtido {numeros}."
    print(f"Perfil Ciência de Dados completo: regras disparadas {numeros}.")

    # Análise com matemática média e SQL: dispara a regra 8, não 7 ou 9.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "analise",
        "ferramenta": "sql", "entrega": "inteligencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [8], f"Análise/SQL: esperada [8], obtido {numeros}."
    print(f"Perfil análise com SQL: regras disparadas {numeros}.")

    # Regra 9 é complementar e independe da atuação diária.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "python", "entrega": "inteligencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [9], f"Python e previsões: esperada [9], obtido {numeros}."
    print(f"Perfil Python e previsões: regras disparadas {numeros}.")

    # Matemática alta + análise, sem interesse em previsões: apenas regra 7.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "analise",
        "ferramenta": "sql", "entrega": "dados",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [7], f"Matemática e análise: esperada [7], obtido {numeros}."
    print(f"Perfil matemática alta e análise: regras disparadas {numeros}.")

    # Matemática baixa não satisfaz a regra 9, mesmo com Python e previsões.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "python", "entrega": "inteligencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Matemática baixa não deveria disparar regras: {numeros}."
    print("Perfil Python, matemática baixa e sem análise: nenhuma regra disparada.")
    print("Regras de Ciência de Dados e ML 7, 8 e 9 validadas nos exemplos!")
    # Engenharia de Dados + SQL + entrega de dados: regras 10 e 11.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "engenharia_dados",
        "ferramenta": "sql", "entrega": "dados",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [10, 11], f"Engenharia de Dados/SQL: esperado [10, 11], obtido {numeros}."
    print(f"Perfil Engenharia de Dados com SQL: regras disparadas {numeros}.")

    # SQL + interesse em pipelines, sem entrega de dados: apenas regra 10.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "engenharia_dados",
        "ferramenta": "sql", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [10], f"Pipelines/SQL: esperado [10], obtido {numeros}."
    print(f"Perfil pipelines com SQL: regras disparadas {numeros}.")

    # Atuação em pipelines + entrega de dados: regra 11 (sem ferramentas associadas).
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "engenharia_dados",
        "ferramenta": "gestao", "entrega": "dados",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [11], f"Pipelines/integração: esperado [11], obtido {numeros}."
    print(f"Perfil pipelines e integração de dados: regras disparadas {numeros}.")

    # Python + matemática média + entrega de dados e interesse em pipelines: 11 e 12.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "engenharia_dados",
        "ferramenta": "python", "entrega": "dados",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [11, 12], f"Python/dados: esperado [11, 12], obtido {numeros}."
    print(f"Perfil Engenharia de Dados com Python: regras disparadas {numeros}.")

    # Docker/CI-CD + matemática alta + entrega de dados: regra 12 sem atuar em pipelines.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "devops", "entrega": "dados",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [12], f"Docker/dados: esperado [12], obtido {numeros}."
    print(f"Perfil Docker/CI-CD e integração de dados: regras disparadas {numeros}.")

    # Afinidade matemática baixa não satisfaz a regra 12.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "python", "entrega": "dados",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Matemática baixa não deveria disparar regra: {numeros}."
    print("Perfil Python e integração de dados, matemática baixa: nenhuma regra disparada.")

    print("Regras de Engenharia de Dados 10, 11 e 12 validadas nos exemplos!")

    # Segurança completa: Linux/Redes + vulnerabilidades + proteção; regras 13, 14 e 15.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "seguranca",
        "ferramenta": "redes", "entrega": "seguranca",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [13, 14, 15], f"Cibersegurança: esperado [13, 14, 15], obtido {numeros}."
    print(f"Perfil completo de Cibersegurança: regras disparadas {numeros}.")

    # Interesse em vulnerabilidades + Linux/Redes, sem entrega de proteção: apenas 13.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "seguranca",
        "ferramenta": "redes", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [13], f"Vulnerabilidades/Redes: esperada [13], obtido {numeros}."
    print(f"Perfil vulnerabilidades com Linux/Redes: regras disparadas {numeros}.")

    # Interesse em vulnerabilidades e entrega de proteção sem Linux/Python: apenas 14.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "seguranca",
        "ferramenta": "gestao", "entrega": "seguranca",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [14], f"Proteção de sistemas: esperada [14], obtido {numeros}."
    print(f"Perfil vulnerabilidades e proteção: regras disparadas {numeros}.")

    # Python e matemática alta com entrega de proteção, sem atuação em segurança: apenas 15.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "python", "entrega": "seguranca",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [15], f"Python/proteção: esperada [15], obtido {numeros}."
    print(f"Perfil Python e proteção, matemática alta: regras disparadas {numeros}.")

    # Linux/Redes e matemática média com entrega de proteção, sem atuação em segurança.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "redes", "entrega": "seguranca",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [15], f"Redes/proteção: esperada [15], obtido {numeros}."
    print(f"Perfil Linux/Redes e proteção, matemática média: regras disparadas {numeros}.")

    # Matemática baixa não satisfaz a regra 15 sem atuação em segurança.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "python", "entrega": "seguranca",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Matemática baixa sem atuação em segurança: obtido {numeros}."
    print("Perfil Python, matemática baixa e sem atuação em segurança: nenhuma regra disparada.")

    # Redes sem atuação em segurança não geram regras de Cibersegurança;
    # atuação em Produtos e entrega de negócios ativam regra 29.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "redes", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"Redes sem segurança, com atuação em Produtos: esperado [29], obtido {numeros}."
    print("Perfil com Linux/Redes e foco em Produtos: nenhuma regra Cibersegurança; regra 29 disparada.")

    print("Regras de Cibersegurança 13, 14 e 15 validadas nos exemplos!")

    # DevOps completo: atuação em automação + Docker/CI-CD + entrega de automação.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "devops",
        "ferramenta": "devops", "entrega": "automacao",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [16, 17, 18], f"DevOps completo: esperado [16, 17, 18], obtido {numeros}."
    print(f"Perfil completo DevOps & SRE: regras disparadas {numeros}.")

    # Automação + Docker/CI-CD sem entrega de automação: somente regra 16.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "devops",
        "ferramenta": "devops", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [16], f"DevOps/Docker sem entrega: esperado [16], obtido {numeros}."
    print(f"Perfil DevOps com Docker/CI-CD: regras disparadas {numeros}.")

    # Atuação e entrega orientadas à automação sem Docker: somente regra 17.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "devops",
        "ferramenta": "gestao", "entrega": "automacao",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [17], f"DevOps sem Docker: esperado [17], obtido {numeros}."
    print(f"Perfil automação e confiabilidade: regras disparadas {numeros}.")

    # Ferramentas Docker/CI-CD e entrega de automação, sem atuação em DevOps: regra 18.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "devops", "entrega": "automacao",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [18], f"Docker/automação: esperado [18], obtido {numeros}."
    print(f"Perfil Docker/CI-CD e entrega de automação: regras disparadas {numeros}.")

    # Linux/Redes não substitui Docker/CI-CD nas regras 16 e 18.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "devops",
        "ferramenta": "redes", "entrega": "automacao",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [17], f"DevOps/Redes: esperado [17], obtido {numeros}."
    print(f"Perfil DevOps com Linux/Redes: regras disparadas {numeros}.")

    # Docker/CI-CD sem atuação/entrega DevOps não deve ativar DevOps;
    # atuação em Produtos e entrega de negócios ativam regra 29.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "devops", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"Docker sem DevOps, com foco em Produtos: esperado [29], obtido {numeros}."
    print("Perfil Docker/CI-CD com foco em Produtos: nenhuma regra DevOps; regra 29 disparada.")

    # Python e entrega de automação sem atuação DevOps também não bastam.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "python", "entrega": "automacao",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Python isolado não deve ativar regras DevOps: {numeros}."
    print("Perfil Python sem foco em DevOps: nenhuma regra disparada.")

    print("Regras de DevOps & SRE 16, 17 e 18 validadas nos exemplos!")
    # AWS/Azure/GCP + atuação em nuvem + entrega de infraestrutura: 19 e 20.
    # Não ativa 21, que exige ferramenta complementar Linux/Redes ou Docker/CI-CD.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "cloud",
        "ferramenta": "cloud", "entrega": "infraestrutura",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [19, 20], f"Cloud completo: esperado [19, 20], obtido {numeros}."
    print(f"Perfil Cloud com AWS/Azure/GCP: regras disparadas {numeros}.")

    # Infraestrutura em nuvem + AWS/Azure/GCP, sem entrega de infraestrutura: 19.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "cloud",
        "ferramenta": "cloud", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [19], f"Cloud/AWS sem entrega: esperado [19], obtido {numeros}."
    print(f"Perfil Cloud com AWS sem entrega de infraestrutura: regras disparadas {numeros}.")

    # Atuação em Cloud + entrega de infraestrutura, sem ferramenta Cloud: 20.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "cloud",
        "ferramenta": "gestao", "entrega": "infraestrutura",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [20], f"Cloud/infraestrutura: esperado [20], obtido {numeros}."
    print(f"Perfil Cloud com foco em escalabilidade: regras disparadas {numeros}.")

    # Linux/Redes + matemática média + infraestrutura, sem atuação em nuvem: 21.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "redes", "entrega": "infraestrutura",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [21], f"Redes e infraestrutura: esperado [21], obtido {numeros}."
    print(f"Perfil Linux/Redes e infraestrutura: regras disparadas {numeros}.")

    # Docker/Kubernetes/CI-CD + matemática alta + infraestrutura: 21.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "devops", "entrega": "infraestrutura",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [21], f"Docker e infraestrutura: esperado [21], obtido {numeros}."
    print(f"Perfil Docker/CI-CD e infraestrutura: regras disparadas {numeros}.")

    # Atuação Cloud + Linux/Redes + matemática média + infraestrutura: 20 e 21.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "cloud",
        "ferramenta": "redes", "entrega": "infraestrutura",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [20, 21], f"Cloud/Redes: esperado [20, 21], obtido {numeros}."
    print(f"Perfil Cloud com Linux/Redes: regras disparadas {numeros}.")

    # Matemática baixa não satisfaz a regra 21.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "redes", "entrega": "infraestrutura",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Matemática baixa não deve disparar 21: {numeros}."
    print("Perfil Redes, matemática baixa, sem atuar em Cloud: nenhuma regra disparada.")

    # AWS/Azure/GCP sem atuação/entrega Cloud não dispara regras Cloud;
    # atuar em Produtos e entregar negócio aciona regra 29.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "cloud", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"AWS sem Cloud, com foco em Produtos: esperado [29], obtido {numeros}."
    print("Perfil AWS/Azure/GCP com foco em Produtos: nenhuma regra Cloud; regra 29 disparada.")

    print("Regras de Cloud Architecture 19, 20 e 21 validadas nos exemplos!")
    # Perfil completo Mobile: atuação, tecnologia específica e entrega de apps.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "mobile",
        "ferramenta": "mobile", "entrega": "mobile",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [22, 23, 24], f"Mobile completo: esperado [22, 23, 24], obtido {numeros}."
    print(f"Perfil Mobile completo: regras disparadas {numeros}.")

    # Atuação em Mobile + ferramentas Mobile, sem entrega de apps: apenas 22.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "mobile",
        "ferramenta": "mobile", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [22], f"Mobile/ferramentas: esperado [22], obtido {numeros}."
    print(f"Perfil Mobile com Flutter/React Native, sem entrega mobile: regras disparadas {numeros}.")

    # Atuação Mobile + entrega Mobile, sem ferramenta específica: apenas 23.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "mobile",
        "ferramenta": "sql", "entrega": "mobile",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [23], f"Mobile/entrega: esperado [23], obtido {numeros}."
    print(f"Perfil Mobile com foco em aplicativos do cotidiano: regras disparadas {numeros}.")

    # JavaScript + entrega Mobile, mesmo sem escolher a atuação Mobile: apenas 24.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "javascript", "entrega": "mobile",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [24], f"JavaScript/Mobile: esperado [24], obtido {numeros}."
    print(f"Perfil JavaScript e entrega de aplicativos: regras disparadas {numeros}.")

    # Ferramenta Mobile + entrega Mobile, sem atuação Mobile: apenas 24.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "mobile", "entrega": "mobile",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [24], f"Ferramenta/entrega Mobile: esperado [24], obtido {numeros}."
    print(f"Perfil com tecnologia Mobile e entrega de aplicativos: regras disparadas {numeros}.")

    # Atuação Mobile + JavaScript + entrega Mobile: regras 23 e 24.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "mobile",
        "ferramenta": "javascript", "entrega": "mobile",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [23, 24], f"Mobile/JavaScript: esperado [23, 24], obtido {numeros}."
    print(f"Perfil Mobile com JavaScript e entrega de apps: regras disparadas {numeros}.")

    # Ferramenta Mobile sem atuação/entrega Mobile NÃO dispara regras Mobile;
    # atuação em Produtos e entrega de negócio ativam regra 29.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "mobile", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"Ferramenta Mobile sem foco Mobile, com gestão de produto: esperado [29], obtido {numeros}."
    print("Perfil tecnologia Mobile com foco em Produtos: nenhuma regra Mobile; regra 29 disparada.")

    # Entrega Mobile isolada também não satisfaz as regras cruzadas.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "sql", "entrega": "mobile",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Entrega Mobile isolada não deve disparar regra: {numeros}."
    print("Perfil apenas com entrega de aplicativos: nenhuma regra disparada.")

    print("Regras de Desenvolvimento Mobile 22, 23 e 24 validadas nos exemplos!")

    # Perfil completo QA: atuação em testes, ferramenta de automação e qualidade.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "qa",
        "ferramenta": "qa", "entrega": "qualidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [25, 26, 27], f"QA completo: esperado [25, 26, 27], obtido {numeros}."
    print(f"Perfil QA completo: regras disparadas {numeros}.")

    # Atuação em QA + ferramenta QA, sem foco na entrega de qualidade: apenas 25.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "qa",
        "ferramenta": "qa", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [25], f"QA e ferramentas: esperado [25], obtido {numeros}."
    print(f"Perfil QA com Playwright/Selenium/Cypress: regras disparadas {numeros}.")

    # Atuação em QA + entrega de qualidade, sem ferramenta técnica: apenas 26.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "qa",
        "ferramenta": "nenhuma", "entrega": "qualidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [26], f"Atuação/qualidade: esperado [26], obtido {numeros}."
    print(f"Perfil QA iniciante e entrega de qualidade: regras disparadas {numeros}.")

    # Python + entrega de qualidade mesmo sem atuação em QA: apenas 27.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "python", "entrega": "qualidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [27], f"Python/qualidade: esperado [27], obtido {numeros}."
    print(f"Perfil Python e qualidade: regras disparadas {numeros}.")

    # JavaScript/TypeScript + entrega de qualidade, sem atuação QA: apenas 27.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "javascript", "entrega": "qualidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [27], f"JavaScript/qualidade: esperado [27], obtido {numeros}."
    print(f"Perfil JavaScript e qualidade: regras disparadas {numeros}.")

    # Ferramentas de QA + entrega de qualidade, sem atuação QA: apenas 27.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "qa", "entrega": "qualidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [27], f"Ferramenta QA/qualidade: esperado [27], obtido {numeros}."
    print(f"Perfil ferramenta QA e qualidade: regras disparadas {numeros}.")

    # Atuação QA + JavaScript + qualidade: regras 26 e 27, não 25.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "qa",
        "ferramenta": "javascript", "entrega": "qualidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [26, 27], f"QA com JS: esperado [26, 27], obtido {numeros}."
    print(f"Perfil QA com JavaScript e qualidade: regras disparadas {numeros}.")

    # Ferramentas QA sem foco em testes ou qualidade não ativam QA;
    # atuação em Produtos e entrega de negócios ativam regra 29.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "qa", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"Ferramenta QA sem atuação QA, com produto: esperado [29], obtido {numeros}."
    print("Perfil com ferramenta QA e foco em Produtos: nenhuma regra QA; regra 29 disparada.")

    # Apenas entrega de qualidade sem atuação ou ferramentas QA: nenhuma regra.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "nenhuma", "entrega": "qualidade",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Entrega de qualidade isolada não deveria disparar regra: {numeros}."
    print("Perfil apenas com entrega de qualidade: nenhuma regra disparada.")

    print("Regras de Engenharia de Qualidade e Testes (QA) 25, 26 e 27 validadas nos exemplos!")
    # Gestão de Produtos — perfil completo deve disparar as três regras.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "gestao", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [28, 29, 30], f"Produtos completo: esperado [28, 29, 30], obtido {numeros}."
    print(f"Perfil Gestão de Produtos completo: regras disparadas {numeros}.")

    # Planejamento + Jira/Trello/Figma sem entrega estratégica: apenas 28.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "gestao", "entrega": "mobile",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [28], f"Planejamento e ferramenta de gestão: esperado [28], obtido {numeros}."
    print(f"Perfil planejamento com Jira/Trello/Figma: regras disparadas {numeros}.")

    # Planejamento + estratégia de negócio sem ferramenta: apenas 29.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "nenhuma", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"Planejamento e negócios: esperado [29], obtido {numeros}."
    print(f"Perfil iniciante em Gestão de Produtos: regras disparadas {numeros}.")

    # Ferramenta de gestão + entrega negócio sem atuar em Produtos: apenas 30.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "qa",
        "ferramenta": "gestao", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [30], f"Gestão e negócio sem atuação de Produto: esperado [30], obtido {numeros}."
    print(f"Perfil Jira/Trello/Figma com entrega de negócios: regras disparadas {numeros}.")

    # Plano de negócio com linguagem JavaScript, sem ferramentas de gestão: 29.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "javascript", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [29], f"Produto com JavaScript: esperado [29], obtido {numeros}."
    print(f"Perfil Gestão de Produtos com JavaScript: regras disparadas {numeros}.")

    # Atuação em produto com Figma, mas entrega visual: dispara 6 (Front-end) e 28.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "gestao", "entrega": "experiencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [6, 28], f"Produto + design: esperado [6, 28], obtido {numeros}."
    print(f"Perfil Produtos com entrega visual: regras disparadas {numeros}.")

    # Ferramentas de gestão isoladas não bastam para acionar Gestão de Produtos.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "qa",
        "ferramenta": "gestao", "entrega": "dados",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [], f"Ferramenta de gestão isolada: nenhuma regra esperada; obtido {numeros}."
    print("Perfil apenas com Jira/Trello/Figma: nenhuma regra disparada.")

    # Somente entrega de negócios não é suficiente para ativar regras de Produto.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "qa",
        "ferramenta": "nenhuma", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [], f"Somente entrega negócio: nenhuma regra esperada; obtido {numeros}."
    print("Perfil apenas com entrega de negócios: nenhuma regra disparada.")

    # Valida registro rastreável de regras e motivos cadastrados na Fase 1.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "gestao", "entrega": "negocios",
    })
    motor.run()
    ids = sorted(regra.numero for regra in motor.regras_disparadas)
    assert ids == [28, 29, 30], f"Registro das regras de Gestão de Produtos incorreto: {ids}."
    assert all(regra.motivo for regra in motor.regras_disparadas), "Faltam justificativas."
    print("Regras de Gestão de Produtos 28, 29 e 30 validadas nos exemplos!")
    print("Todas as 30 regras cadastradas e validadas nos exemplos!")

    # Pontuação: cada resposta contribui uma vez por carreira, independentemente
    # da quantidade de regras disparadas. A validação usa os pesos da Fase 1.
    sem_perfil = MotorInferencia()
    try:
        sem_perfil.calcular_pontuacoes()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Pontuação sem perfil deveria falhar.")

    casos_pontuacao = (
        (
            "Back-end completo",
            {"matematica": "media", "atuacao": "logica",
             "ferramenta": "java", "entrega": "funcionalidade"},
            "backend", (1, 5, 3, 0, 5), 14,
        ),
        (
            "Front-end completo",
            {"matematica": "baixa", "atuacao": "interfaces",
             "ferramenta": "javascript", "entrega": "experiencia"},
            "frontend_uiux", (0, 5, 3, 0, 5), 13,
        ),
        (
            "Ciência de Dados com matemática alta",
            {"matematica": "alta", "atuacao": "analise",
             "ferramenta": "python", "entrega": "inteligencia"},
            "ciencia_dados_ml", (2, 5, 3, 0, 5), 15,
        ),
        (
            "QA iniciante sem ferramenta",
            {"matematica": "baixa", "atuacao": "qa",
             "ferramenta": "nenhuma", "entrega": "qualidade"},
            "engenharia_qa", (0, 5, 0, 0, 5), 10,
        ),
        (
            "Cloud com matemática baixa",
            {"matematica": "baixa", "atuacao": "cloud",
             "ferramenta": "cloud", "entrega": "infraestrutura"},
            "cloud_architecture", (0, 5, 3, 0, 5), 13,
        ),
        (
            "Mobile sem pontuação matemática",
            {"matematica": "alta", "atuacao": "mobile",
             "ferramenta": "mobile", "entrega": "mobile"},
            "desenvolvimento_mobile", (0, 5, 3, 0, 5), 13,
        ),
    )
    for nome, respostas, codigo, componentes, total_esperado in casos_pontuacao:
        motor.registrar_perfil(respostas)
        motor.run()
        resultados = motor.calcular_pontuacoes()
        assert len(resultados) == 10, "Pontuação deve incluir as 10 carreiras."
        assert len({p.codigo_trilha for p in resultados}) == 10
        pontos = next(p for p in resultados if p.codigo_trilha == codigo)
        detalhamento = (
            pontos.matematica, pontos.atuacao,
            pontos.ferramenta_principal, pontos.ferramenta_complementar,
            pontos.entrega,
        )
        assert detalhamento == componentes, (
            f"{nome}: esperado {componentes}, obtido {detalhamento}."
        )
        assert pontos.total == total_esperado, (
            f"{nome}: esperado {total_esperado} pontos, obtido {pontos.total}."
        )
        assert all(p.ferramenta_principal == 0 or p.ferramenta_complementar == 0
                   for p in resultados), "Ferramenta não pode pontuar em duas classes."
        print(f"Pontuação validada — {nome}: {pontos.total} pontos.")

    # A seção de pontuação preserva o teste do empate, sem decidir seu vencedor.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "devops",
        "ferramenta": "redes", "entrega": "infraestrutura",
    })
    motor.run()
    pontuacoes = {p.codigo_trilha: p for p in motor.calcular_pontuacoes()}
    assert pontuacoes["devops_sre"].total == 7
    assert pontuacoes["cloud_architecture"].total == 7
    print("Pontuação: empate DevOps/Cloud validado, 7 pontos para cada.")

    # Ao registrar um novo perfil, a pontuação anterior não pode persistir.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "gestao", "entrega": "negocios",
    })
    motor.run()
    pontuacoes = {p.codigo_trilha: p for p in motor.calcular_pontuacoes()}
    assert pontuacoes["gestao_produtos"].total == 13
    assert pontuacoes["devops_sre"].total == 0
    print("Registro de novo perfil e ausência de pontuação duplicada: validados!")
    print("Sistema de pontuação validado nos exemplos!")

    # Desempate real: DevOps e Cloud têm sete pontos. A preferência de
    # atuação da pergunta 2 deve priorizar DevOps sem alterar os pontos.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "devops",
        "ferramenta": "redes", "entrega": "infraestrutura",
    })
    motor.run()
    antes_regras = tuple(motor.regras_disparadas)
    antes_pontuacoes = motor.calcular_pontuacoes()
    resultado = motor.resolver_desempate()
    assert resultado is not None
    assert resultado.codigo_selecionado == "devops_sre"
    assert resultado.criterio_decisivo == "atuacao"
    assert resultado.pontuacao_empatada == 7
    assert set(resultado.candidatos_originais) == {"devops_sre", "cloud_architecture"}
    assert motor.calcular_pontuacoes() == antes_pontuacoes
    assert tuple(motor.regras_disparadas) == antes_regras
    print("Desempate real DevOps/Cloud: atuação priorizou DevOps (7 pontos cada).")

    # Sem empate na maior pontuação, o método não altera a classificação.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "analise",
        "ferramenta": "python", "entrega": "inteligencia",
    })
    motor.run()
    assert motor.resolver_desempate() is None
    print("Perfil sem empate: nenhum desempate aplicado (correto).")

    # Testes isolados para as quatro prioridades, com totais empatados.
    # Os perfis reais normalmente se resolvem logo pela atuação (P2).
    # As pontuações artificiais abaixo validam o restante da ordem.
    def pontos(codigo: str, *, mat: int = 0, atu: int = 0,
               principal: int = 0, complementar: int = 0,
               entrega: int = 0) -> PontuacaoTrilha:
        return PontuacaoTrilha(
            codigo_trilha=codigo, nome_trilha=codigo,
            matematica=mat, atuacao=atu,
            ferramenta_principal=principal,
            ferramenta_complementar=complementar, entrega=entrega,
        )

    cenarios_isolados = (
        (
            "entrega",
            (pontos("ganhador", entrega=5), pontos("outro", mat=2, principal=3)),
        ),
        (
            "ferramenta_principal",
            (pontos("ganhador", principal=3),
             pontos("outro", mat=2, complementar=1)),
        ),
        (
            "matematica",
            (pontos("ganhador", mat=2),
             pontos("outro", mat=1, complementar=1)),
        ),
    )
    for criterio, pontuacoes_teste in cenarios_isolados:
        empate = MotorInferencia._desempatar_pontuacoes(pontuacoes_teste)
        assert empate is not None
        assert empate.criterio_decisivo == criterio
        assert empate.codigo_selecionado == "ganhador"
        assert empate.pontuacao_empatada == pontuacoes_teste[0].total
        print(f"Critério de desempate isolado validado: {criterio}.")

    # Sem correspondência em nenhuma das quatro prioridades, sinaliza
    # impossibilidade em vez de escolher arbitrariamente uma carreira.
    try:
        MotorInferencia._desempatar_pontuacoes(
            (pontos("a", principal=3), pontos("b", principal=3))
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("Empate persistente deve ser sinalizado.")
    print("Empate persistente: erro explícito validado (sem critério extra).")
    print("Quatro prioridades aprovadas de desempate validadas nos exemplos!")
    # Etapa 2.90 — Recomendação final rastreável, preservando todos os testes.
    # Execução direta sem chamar motor.run() também deve registrar as regras.
    sem_perfil_recomendacao = MotorInferencia()
    try:
        sem_perfil_recomendacao.recomendar_carreira()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Recomendação sem perfil deveria falhar.")

    casos_recomendacao = (
        (
            "Back-end completo",
            {"matematica": "media", "atuacao": "logica",
             "ferramenta": "java", "entrega": "funcionalidade"},
            "backend", 14, (1, 2),
        ),
        (
            "Front-end completo",
            {"matematica": "baixa", "atuacao": "interfaces",
             "ferramenta": "javascript", "entrega": "experiencia"},
            "frontend_uiux", 13, (4, 5),
        ),
        (
            "Ciência de Dados completo",
            {"matematica": "alta", "atuacao": "analise",
             "ferramenta": "python", "entrega": "inteligencia"},
            "ciencia_dados_ml", 15, (7, 8, 9),
        ),
        (
            "QA iniciante",
            {"matematica": "baixa", "atuacao": "qa",
             "ferramenta": "nenhuma", "entrega": "qualidade"},
            "engenharia_qa", 10, (26,),
        ),
        (
            "Gestão de Produtos completa",
            {"matematica": "baixa", "atuacao": "produto",
             "ferramenta": "gestao", "entrega": "negocios"},
            "gestao_produtos", 13, (28, 29, 30),
        ),
    )
    for nome, respostas, codigo_esperado, total_esperado, regras_esperadas in casos_recomendacao:
        motor.registrar_perfil(respostas)
        recomendacao = motor.recomendar_carreira()
        assert recomendacao.codigo_trilha == codigo_esperado, nome
        assert recomendacao.pontuacao_total == total_esperado, nome
        assert recomendacao.desempate is None, nome
        assert tuple(r.numero for r in recomendacao.regras_da_trilha) == regras_esperadas, nome
        assert recomendacao.pontuacao_total == sum((
            recomendacao.detalhamento.matematica,
            recomendacao.detalhamento.atuacao,
            recomendacao.detalhamento.ferramenta_principal,
            recomendacao.detalhamento.ferramenta_complementar,
            recomendacao.detalhamento.entrega,
        )), nome
        assert recomendacao.justificativas_pontuacao, nome
        assert recomendacao.nome_trilha in recomendacao.formatar(), nome
        assert all(f"Regra {r.numero}: {r.motivo}" in recomendacao.formatar()
                   for r in recomendacao.regras_da_trilha), nome
        # Repetir a consulta não cria pontos ou regras duplicados.
        outra = motor.recomendar_carreira()
        assert recomendacao == outra, f"Consulta duplicada: {nome}"
        print(f"Recomendação validada — {nome}: {total_esperado} pontos.")

    # Empate entre DevOps e Cloud: prioriza atuação sem inventar disparos.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "devops",
        "ferramenta": "redes", "entrega": "infraestrutura",
    })
    recomendacao_empate = motor.recomendar_carreira()
    assert recomendacao_empate.codigo_trilha == "devops_sre"
    assert recomendacao_empate.desempate is not None
    assert recomendacao_empate.desempate.criterio_decisivo == "atuacao"
    assert recomendacao_empate.pontuacao_total == 7
    assert not recomendacao_empate.regras_da_trilha
    assert 21 in {r.numero for r in recomendacao_empate.regras_de_outras_trilhas}
    assert "Nenhuma regra cruzada dessa carreira foi disparada" in recomendacao_empate.formatar()
    assert "Desempate:" in recomendacao_empate.formatar()
    print("Recomendação com empate DevOps/Cloud validada, sem inventar regras disparadas.")
    print("Todas as recomendações, justificativas e rastreabilidade validadas nos exemplos!")
    print("Fase 2 — recomendação final pronta para revisão e publicação no GitHub.")

