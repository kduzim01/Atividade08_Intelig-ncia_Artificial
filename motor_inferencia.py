"""Estrutura inicial do motor de inferência do Consultor de Carreiras em TI.

Atividade Aula 08 — Fase 2, etapa 2.12.

Nesta etapa, o módulo:
- importa e valida a base de conhecimento da Fase 1;
- define um fato Experta com as quatro respostas do usuário;
- valida as alternativas e declara esse fato no motor.

As 30 regras @Rule, a pontuação, os desempates e as recomendações serão
implementados e testados nas próximas etapas, mediante autorização.
"""

from __future__ import annotations

import collections
import collections.abc

# Compatibilidade temporária do frozendict 1.2 (Experta 1.9.4) com Python 3.12.
# O ajuste ocorre apenas neste processo; não modifica bibliotecas instaladas.
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

from experta import Fact, KnowledgeEngine

from base_conhecimento import PERGUNTAS, validar_base_conhecimento


class PerfilUsuario(Fact):
    """Fato com as quatro respostas da entrevista, usando os códigos da Fase 1."""


class MotorInferencia(KnowledgeEngine):
    """Estrutura do motor; ainda não contém regras de recomendação."""

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

        # Reinicia os fatos antes de registrar uma nova entrevista.
        self.reset()
        self.declare(PerfilUsuario(**respostas))


if __name__ == "__main__":
    # Exemplo de entrada usado apenas para verificar o registro dos fatos.
    respostas_exemplo = {
        "matematica": "media",
        "atuacao": "qa",
        "ferramenta": "qa",
        "entrega": "qualidade",
    }

    motor = MotorInferencia()
    motor.registrar_perfil(respostas_exemplo)

    perfis = [
        fato for fato in motor.facts.values()
        if isinstance(fato, PerfilUsuario)
    ]
    assert len(perfis) == 1, "Deveria existir um único fato de perfil."

    print("Motor inicializado e base validada com sucesso!")
    print("Fato PerfilUsuario registrado com as quatro respostas.")
    print("Regras de recomendação ainda não implementadas (etapas futuras).")
