"""Verifica isolamento do teste, ausência de vazamento e invariantes dos dados reais."""

import json
import csv
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from utils import ATRIBUTOS, ROOT, carregar_dados, iterar_folds, preparar_particao


class TestPreparacao(unittest.TestCase):
    def setUp(self):
        self.train = pd.DataFrame({
            "id": ["a", "b", "c", "d"], "ano": [2024] * 4, "frp": [10., 20., 30., 40.],
            "numero_dias_sem_chuva": [1., 2., 3., np.nan], "precipitacao": [0., 1., 2., 3.],
            "lat": [-3.] * 4, "lon": [-60.] * 4, "mes": [1, 2, 3, 4], "hora_utc": [17.] * 4})
        self.valid = self.train.iloc[:2].copy()
        self.valid["id"] = ["e", "f"]
        self.valid["numero_dias_sem_chuva"] = [np.nan, 1000.]
        self.valid["frp"] = [0., 100_000.]

    def test_estatisticas_usam_apenas_treino(self):
        p = preparar_particao(self.train, self.valid)
        self.assertEqual(p.limiar_frp, 32.5)
        self.assertEqual(p.parametros["medianas"]["numero_dias_sem_chuva"], 2.)
        self.assertEqual(p.parametros["medias"]["numero_dias_sem_chuva"], 2.)
        self.assertEqual(p.X_avaliacao.iloc[0]["numero_dias_sem_chuva"], 0.)
        self.assertEqual(p.y_cls_treino.tolist(), [0, 0, 0, 1])
        self.assertEqual(p.y_cls_avaliacao.tolist(), [0, 1])
        self.assertEqual(p.X_treino.lat.tolist(), [0.] * 4)
        self.assertEqual(list(p.X_treino.columns), ATRIBUTOS)
        self.assertTrue(pd.isna(self.train.iloc[3].numero_dias_sem_chuva))

    def test_alterar_avaliacao_nao_altera_parametros(self):
        first = preparar_particao(self.train, self.valid)
        changed = self.valid.copy()
        changed[ATRIBUTOS] = 1e9
        changed["frp"] = 1e12
        second = preparar_particao(self.train, changed)
        self.assertEqual(first.parametros, second.parametros)
        self.assertEqual(first.limiar_frp, second.limiar_frp)
        pd.testing.assert_frame_equal(first.X_treino, second.X_treino)

    def test_discretizacao_usa_corte_do_treino(self):
        p = preparar_particao(self.train, self.valid, "discretizada")
        self.assertEqual(p.parametros["cortes"]["numero_dias_sem_chuva"], 2.)
        self.assertEqual(p.X_avaliacao.numero_dias_sem_chuva.tolist(), [1, 1])
        self.assertTrue(set(np.unique(p.X_treino)) <= {0, 1})

    def test_rejeita_ids_compartilhados(self):
        with self.assertRaisesRegex(ValueError, "identificadores compartilhados"):
            preparar_particao(self.train, self.train.iloc[:1])

    def test_rejeita_ajuste_com_2025(self):
        changed = self.train.copy()
        changed["ano"] = 2025
        with self.assertRaisesRegex(ValueError, "exclusivamente 2024"):
            preparar_particao(changed, self.valid)

    def test_nao_imputa_alvo(self):
        changed = self.train.copy()
        changed.loc[0, "frp"] = np.nan
        with self.assertRaisesRegex(ValueError, "alvo não é imputado"):
            preparar_particao(changed, self.valid)


class TestDatasetReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = carregar_dados(2024)
        cls.test = carregar_dados(2025)
        cls.audit = json.loads((ROOT / "docs/auditoria-dataset.json").read_text())

    def test_filtros_e_identidade(self):
        combined = pd.concat([self.dev, self.test])
        self.assertFalse(combined.id.duplicated().any())
        self.assertFalse(combined.duplicated(["lat", "lon", "data_hora_gmt", "satelite"]).any())
        self.assertTrue(combined.bioma.eq("Amazônia").all())
        self.assertTrue(combined.pais.eq("Brasil").all())
        self.assertTrue(combined.satelite.eq("AQUA_M-T").all())
        self.assertTrue(np.isfinite(combined.frp).all())
        self.assertTrue(combined.frp.ge(0).all())
        self.assertTrue(combined.data_hora_gmt.dt.year.eq(combined.ano).all())
        self.assertTrue(combined.data_hora_gmt.dt.month.eq(combined.mes).all())
        self.assertEqual(set(combined.arquivo_origem), {
            f"focos_mensal_br_{year}{month:02d}.csv" for year in (2024, 2025) for month in range(1, 13)})
        self.assertEqual(len(combined), self.audit["totais"]["retidas_finais"])

    def test_ausencias_preservadas_e_indicadas(self):
        for frame in (self.dev, self.test):
            for col in ("numero_dias_sem_chuva", "precipitacao"):
                self.assertTrue(frame[col].isna().eq(frame[col + "_ausente"].eq(1)).all())
            self.assertFalse(frame[ATRIBUTOS].eq(-999).any().any())

    def test_cinco_folds_espaciais_sem_grupos_compartilhados(self):
        seen = []
        for _, train, valid in iterar_folds(self.dev):
            self.assertFalse(set(train.grupo_validacao) & set(valid.grupo_validacao))
            seen.extend(valid.id.tolist())
            partition = preparar_particao(train, valid)
            self.assertEqual(partition.y_cls_treino.nunique(), 2)
            self.assertEqual(partition.y_cls_avaliacao.nunique(), 2)
            self.assertTrue(np.isfinite(partition.X_treino).all().all())
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(set(seen), set(self.dev.id))

    def test_temporal_e_teste_externo(self):
        for _, train, valid in iterar_folds(self.dev, "temporal"):
            self.assertLess(train.data_hora_gmt.max(), valid.data_hora_gmt.min())
            self.assertTrue(train.ano.eq(2024).all() and valid.ano.eq(2024).all())
        self.assertTrue(self.test.fold_espacial.isna().all())
        self.assertLess(self.dev.data_hora_gmt.max(), self.test.data_hora_gmt.min())
        self.assertNotIn("estatisticas_frp", self.audit["anos"]["2025"])
        with self.assertRaisesRegex(ValueError, "exclusivamente 2024"):
            list(iterar_folds(self.test))

    def test_dicionario_e_conferencia_com_produto_anual(self):
        with (ROOT / "data/dicionario.csv").open(newline="") as stream:
            dictionary = list(csv.DictReader(stream))
        self.assertEqual(len(dictionary), 27)
        self.assertEqual({row["coluna"] for row in dictionary}, set(self.dev.columns))
        pilot = json.loads((ROOT / "docs/perfil-dados.json").read_text())
        annual = {int(row["arquivo"][13:17]): row["linhas_amazonia"]
                  for row in pilot["arquivos"] if row["arquivo"].startswith("focos_br_ref_")}
        self.assertEqual(len(self.dev), annual[2024])
        self.assertEqual(len(self.test), annual[2025])


if __name__ == "__main__":
    unittest.main()
