"""Motor de inferência do Consultor Inteligente de Carreiras em TI.

Atividade Aula 08 — Fase 2, etapa 2.60.

Preserva integralmente as regras 1 a 21 e acrescenta as regras 22 a 24 de
Desenvolvimento Mobile. Os disparos são registrados para futuras justificativas.
Pontuação, desempate e as demais 6 regras ficam para etapas posteriores.
"""

from __future__ import annotations

import collections
import collections.abc

# Compatibilidade temporária do frozendict 1.2 (Experta 1.9.4) com Python 3.12.
# O ajuste ocorre apenas neste processo; não modifica bibliotecas instaladas.
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

from experta import OR, Fact, KnowledgeEngine, Rule

from base_conhecimento import PERGUNTAS, REGRAS, Regra, validar_base_conhecimento


class PerfilUsuario(Fact):
    """Fato com as quatro respostas da entrevista, usando os códigos da Fase 1."""


class MotorInferencia(KnowledgeEngine):
    """Motor Experta: nesta etapa, executa apenas as regras 1 a 24."""

    def __init__(self) -> None:
        super().__init__()
        self.regras_disparadas: list[Regra] = []

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
        }
        if regra is None or regra.trilha != trilhas_implementadas.get(numero):
            raise ValueError(f"Regra de inferência não encontrada: {numero}.")
        if regra.numero not in {item.numero for item in self.regras_disparadas}:
            self.regras_disparadas.append(regra)

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
    assert not motor.regras_disparadas, "Perfil QA não deve ativar regras Back-end."
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

    # Ferramentas de gestão/design + entrega visual: regra 6, mesmo sem atuação em interfaces.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "gestao", "entrega": "experiencia",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert numeros == [6], f"Ferramenta de design: esperada [6], obtida {numeros}."
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

    # JavaScript, isoladamente, não pode ativar regra Front-end.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "javascript", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"JavaScript isolado não deve disparar regras: {numeros}."
    print("Perfil com JavaScript, sem foco em interfaces: nenhuma regra disparada.")
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

    # Afinidade com redes isolada não deve gerar regra de Cibersegurança.
    motor.registrar_perfil({
        "matematica": "media", "atuacao": "produto",
        "ferramenta": "redes", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Redes isoladas: nenhuma regra esperada; obtido {numeros}."
    print("Perfil apenas com Linux/Redes: nenhuma regra disparada.")

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

    # Apenas afinidade com Docker/CI-CD não deve disparar regra DevOps.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "devops", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Docker/CI-CD isolado não deve ativar regras: {numeros}."
    print("Perfil apenas com Docker/CI-CD: nenhuma regra disparada.")

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

    # Ferramenta AWS/Azure/GCP isolada não dispara regras Cloud.
    motor.registrar_perfil({
        "matematica": "alta", "atuacao": "produto",
        "ferramenta": "cloud", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"AWS isolado não deve disparar regras: {numeros}."
    print("Perfil apenas com AWS/Azure/GCP: nenhuma regra disparada.")

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

    # Uma ferramenta Mobile isolada NÃO basta para recomendar a trilha.
    motor.registrar_perfil({
        "matematica": "baixa", "atuacao": "produto",
        "ferramenta": "mobile", "entrega": "negocios",
    })
    motor.run()
    numeros = sorted(regra.numero for regra in motor.regras_disparadas)
    assert not numeros, f"Ferramenta Mobile isolada não deve disparar regra: {numeros}."
    print("Perfil apenas com tecnologias Mobile: nenhuma regra disparada.")

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
    print("Outras 6 regras, pontuação e recomendações: etapas futuras.")

