"""Motor de inferência do Consultor Inteligente de Carreiras em TI.

Atividade Aula 08 — Fase 2, etapa 2.18.

Esta entrega mantém o registro e a validação do perfil da etapa anterior
e acrescenta somente as três regras de Desenvolvimento Back-end (1, 2 e 3).
Os disparos são registrados para futuras justificativas. Pontuação,
desempate e as outras 27 regras ficam para etapas posteriores.
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
    """Motor Experta: nesta etapa, executa apenas as regras 1 a 3 (Back-end)."""

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
        if regra is None or regra.trilha != "backend":
            raise ValueError(f"Regra de Back-end não encontrada: {numero}.")
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
    print("Outras 27 regras, pontuação e recomendações: etapas futuras.")
