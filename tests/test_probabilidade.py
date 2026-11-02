"""Verifica as funções de probabilidade da Etapa 3 com casos de resposta conhecida."""

import unittest

import numpy as np

from probabilidade import (bayes, bayes_binario, binarizar, conjunta, condicional,
                           contagens_conjuntas, diferenca_risco_por_grupo,
                           independencia_condicional, informacao_mutua, marginal, phi,
                           qui_quadrado_2x2, reconstruir_pela_cadeia)


class TestProbabilidadeBasica(unittest.TestCase):
    def setUp(self):
        self.a = np.array([0, 0, 0, 1, 1, 1, 1, 1])
        self.b = np.array([0, 0, 1, 0, 1, 1, 1, 1])

    def test_conjunta_soma_um_e_marginais(self):
        j = conjunta(self.a, self.b)
        self.assertEqual(j.shape, (2, 2))
        self.assertAlmostEqual(j.sum(), 1.0)
        np.testing.assert_allclose(marginal(j, (0,)), [3 / 8, 5 / 8])
        np.testing.assert_allclose(marginal(j, (1, 0)), j.T)

    def test_condicional_soma_um_por_coluna(self):
        j = conjunta(self.a, self.b)
        c = condicional(j, (1,), (0,))
        np.testing.assert_allclose(c.sum(axis=0), 1.0)
        self.assertAlmostEqual(c[1, 1], 4 / 5)

    def test_condicional_de_evento_impossivel_e_nan(self):
        c = condicional(conjunta([0, 0, 1], [0, 1, 1]), (1,), (0,))
        self.assertFalse(np.isnan(c).any())
        j = conjunta([0, 0, 0], [0, 1, 1])
        self.assertTrue(np.isnan(condicional(j, (1,), (0,))[:, 1]).all())

    def test_regra_da_cadeia_em_qualquer_ordem(self):
        g = np.random.default_rng(1)
        x, y, z = (g.integers(0, 2, 300) for _ in range(3))
        j = conjunta(x, y, z)
        for ordem in [(0, 1, 2), (2, 1, 0), (1, 2, 0)]:
            np.testing.assert_allclose(reconstruir_pela_cadeia(j, ordem), j, atol=1e-12)
        with self.assertRaises(ValueError):
            reconstruir_pela_cadeia(j, (0, 1))

    def test_bayes_exemplo_da_especificacao(self):
        self.assertAlmostEqual(bayes(0.8, 0.05, 0.15), 0.8 * 0.05 / 0.15)
        self.assertAlmostEqual(bayes_binario(0.8, 0.11 / 0.95, 0.05), bayes(0.8, 0.05, 0.15))
        with self.assertRaises(ValueError):
            bayes(0.5, 0.5, 0.0)

    def test_entradas_invalidas(self):
        for chamada in (lambda: conjunta([0, 2], [0, 1]), lambda: conjunta([0, 1], [0]),
                        lambda: conjunta([]), lambda: binarizar([1.0, np.nan], 0),
                        lambda: marginal(conjunta(self.a, self.b), (0, 0)),
                        lambda: condicional(conjunta(self.a, self.b), (0,), (0,))):
            with self.assertRaises(ValueError):
                chamada()

    def test_binarizar_respeita_o_tipo_de_desigualdade(self):
        np.testing.assert_array_equal(binarizar([0, 0, 1], 0), [1, 1, 1])
        np.testing.assert_array_equal(binarizar([0, 0, 1], 0, estrito=True), [0, 0, 1])


class TestIndependencia(unittest.TestCase):
    def test_produto_de_marginais_tem_dependencia_zero(self):
        contagens = np.array([[12, 18], [28, 42]])
        self.assertAlmostEqual(phi(contagens), 0.0)
        self.assertAlmostEqual(qui_quadrado_2x2(contagens)[0], 0.0)
        self.assertAlmostEqual(informacao_mutua(contagens / contagens.sum()), 0.0)

    def test_dependencia_total(self):
        self.assertAlmostEqual(phi(np.array([[50, 0], [0, 50]])), 1.0)
        self.assertAlmostEqual(informacao_mutua(np.array([[0.5, 0], [0, 0.5]])), 1.0)
        self.assertAlmostEqual(phi(np.array([[0, 50], [50, 0]])), -1.0)

    def test_phi_de_variavel_constante_e_zero(self):
        self.assertEqual(phi(np.array([[10, 20], [0, 0]])), 0.0)

    def test_condicionalmente_independentes_mas_marginalmente_dependentes(self):
        g = np.random.default_rng(0)
        c = g.integers(0, 2, 30000)
        x = (g.random(30000) < np.where(c == 1, 0.8, 0.2)).astype(int)
        y = (g.random(30000) < np.where(c == 1, 0.7, 0.3)).astype(int)
        self.assertGreater(abs(phi(contagens_conjuntas(x, y))), 0.2)
        linhas, teste = independencia_condicional(x, y, c)
        self.assertEqual(len(linhas), 2)
        self.assertTrue(all(abs(l["phi"]) < 0.05 for l in linhas))
        self.assertEqual(teste["graus_liberdade"], 2)

    def test_condicionalmente_dependentes_a_cada_classe(self):
        g = np.random.default_rng(3)
        c = g.integers(0, 2, 5000)
        x = g.integers(0, 2, 5000)
        y = x.copy()
        linhas, teste = independencia_condicional(x, y, c)
        self.assertTrue(all(np.isclose(l["phi"], 1.0) for l in linhas))
        self.assertLess(teste["p_valor"], 1e-6)


class TestBootstrapPorGrupo(unittest.TestCase):
    def test_diferenca_pontual_e_reprodutivel(self):
        g = np.random.default_rng(5)
        grupos = g.integers(0, 40, 4000).astype(str)
        exposto = g.integers(0, 2, 4000)
        alvo = (g.random(4000) < np.where(exposto == 1, 0.35, 0.2)).astype(int)
        esperado = alvo[exposto == 1].mean() - alvo[exposto == 0].mean()
        d1 = diferenca_risco_por_grupo(alvo, exposto, grupos, repeticoes=200)
        d2 = diferenca_risco_por_grupo(alvo, exposto, grupos, repeticoes=200)
        self.assertEqual(d1, d2)
        self.assertAlmostEqual(d1[0], esperado)
        self.assertLess(d1[1], d1[0])
        self.assertGreater(d1[2], d1[0])
        self.assertGreater(d1[1], 0)


if __name__ == "__main__":
    unittest.main()
