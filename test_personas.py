"""Testes automatizados das personas do Consultor de Carreiras em TI.

Execute na pasta principal do projeto:
    python -m unittest -v test_personas.py

Os testes utilizam a base de conhecimento e o motor de inferência reais.
Não alteram os módulos da aplicação nem dependem da interface Streamlit.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from base_conhecimento import REGRAS, TRILHAS, validar_base_conhecimento
from motor_inferencia import MotorInferencia


@dataclass(frozen=True)
class Persona:
    nome: str
    respostas: dict[str, str]
    carreira: str
    pontuacao: int
    regras_da_carreira: tuple[int, ...]
    parcelas: tuple[int, int, int, int, int]


PERSONAS: tuple[Persona, ...] = (
    Persona(
        nome="Perfil analítico",
        respostas={
            "matematica": "alta",
            "atuacao": "analise",
            "ferramenta": "python",
            "entrega": "inteligencia",
        },
        carreira="ciencia_dados_ml",
        pontuacao=15,
        regras_da_carreira=(7, 8, 9),
        parcelas=(2, 5, 3, 0, 5),
    ),
    Persona(
        nome="Perfil de infraestrutura e segurança",
        respostas={
            "matematica": "media",
            "atuacao": "seguranca",
            "ferramenta": "redes",
            "entrega": "seguranca",
        },
        carreira="ciberseguranca",
        pontuacao=14,
        regras_da_carreira=(13, 14, 15),
        parcelas=(1, 5, 3, 0, 5),
    ),
    Persona(
        nome="Perfil visual e front-end",
        respostas={
            "matematica": "baixa",
            "atuacao": "interfaces",
            "ferramenta": "javascript",
            "entrega": "experiencia",
        },
        carreira="frontend_uiux",
        pontuacao=13,
        regras_da_carreira=(4, 5),
        parcelas=(0, 5, 3, 0, 5),
    ),
    Persona(
        nome="Perfil de negócios e produtos",
        respostas={
            "matematica": "baixa",
            "atuacao": "produto",
            "ferramenta": "gestao",
            "entrega": "negocios",
        },
        carreira="gestao_produtos",
        pontuacao=13,
        regras_da_carreira=(28, 29, 30),
        parcelas=(0, 5, 3, 0, 5),
    ),
)


def regras_previstas(respostas: dict[str, str]) -> tuple[int, ...]:
    """Obtém disparos esperados diretamente das condições declarativas."""
    return tuple(
        regra.numero
        for regra in REGRAS
        if all(
            respostas[condicao.dimensao] in condicao.valores
            for condicao in regra.condicoes
        )
    )


class TestarPersonas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        validar_base_conhecimento()

    def conferir_persona(self, motor: MotorInferencia, persona: Persona) -> None:
        motor.registrar_perfil(dict(persona.respostas))
        resultado = motor.recomendar_carreira()

        trilha = next(t for t in TRILHAS if t.codigo == persona.carreira)
        self.assertEqual(resultado.codigo_trilha, persona.carreira)
        self.assertEqual(resultado.nome_trilha, trilha.nome)
        self.assertEqual(resultado.pontuacao_total, persona.pontuacao)
        self.assertEqual(resultado.desempate, None)

        detalhe = resultado.detalhamento
        valores = (
            detalhe.matematica,
            detalhe.atuacao,
            detalhe.ferramenta_principal,
            detalhe.ferramenta_complementar,
            detalhe.entrega,
        )
        self.assertEqual(valores, persona.parcelas)
        self.assertEqual(sum(valores), persona.pontuacao)

        da_carreira = tuple(
            regra.numero for regra in resultado.regras_da_trilha
        )
        self.assertEqual(da_carreira, persona.regras_da_carreira)

        todos_disparos = tuple(sorted(
            regra.numero
            for regra in (
                *resultado.regras_da_trilha,
                *resultado.regras_de_outras_trilhas,
            )
        ))
        self.assertEqual(todos_disparos, regras_previstas(persona.respostas))
        self.assertEqual(
            tuple(sorted(regra.numero for regra in motor.regras_disparadas)),
            todos_disparos,
        )
        self.assertEqual(len(resultado.pontuacoes), 10)
        self.assertEqual(
            len({pontuacao.codigo_trilha for pontuacao in resultado.pontuacoes}),
            10,
        )
        self.assertGreaterEqual(len(resultado.justificativas_pontuacao), 3)

        texto = resultado.formatar()
        self.assertIn(trilha.nome, texto)
        self.assertIn(f"{persona.pontuacao} pontos", texto)
        for numero in persona.regras_da_carreira:
            self.assertIn(f"Regra {numero}:", texto)

    def test_quatro_personas(self) -> None:
        """Cada persona deve receber carreira, pontos e evidências corretos."""
        for persona in PERSONAS:
            with self.subTest(persona=persona.nome):
                self.conferir_persona(MotorInferencia(), persona)

    def test_troca_de_perfil_sem_reutilizar_disparos(self) -> None:
        """O mesmo motor não deve herdar fatos e regras da entrevista anterior."""
        motor = MotorInferencia()
        for persona in (*PERSONAS, PERSONAS[0]):
            with self.subTest(persona=persona.nome):
                self.conferir_persona(motor, persona)

    def test_recomendacao_exige_perfil(self) -> None:
        with self.assertRaises(RuntimeError):
            MotorInferencia().recomendar_carreira()

    def test_perfil_incompleto_e_rejeitado(self) -> None:
        respostas = dict(PERSONAS[0].respostas)
        respostas.pop("entrega")
        with self.assertRaises(ValueError):
            MotorInferencia().registrar_perfil(respostas)


if __name__ == "__main__":
    unittest.main(verbosity=2)
