"""Carregamento e preparação dos dados para os notebooks, sem ajustar modelos."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SEED = 42
np.random.seed(SEED)
ATRIBUTOS = ["numero_dias_sem_chuva", "precipitacao", "lat", "lon", "mes", "hora_utc"]
ARQUIVOS = {2024: "desenvolvimento_2024.csv.gz", 2025: "teste_2025.csv.gz"}


def carregar_dados(ano=2024, *, verificar_hash=True):
    """Lê somente o ano solicitado. O padrão não abre o teste de 2025."""
    if ano not in ARQUIVOS:
        raise ValueError("Ano deve ser 2024 (desenvolvimento) ou 2025 (teste).")
    path = ROOT / "data/dataset" / ARQUIVOS[ano]
    if verificar_hash:
        manifest = json.loads((ROOT / "data/dataset/manifesto.json").read_text())
        with path.open("rb") as stream:
            checksum = hashlib.file_digest(stream, "sha256").hexdigest()
        if checksum != manifest["arquivos"][path.name]["sha256"]:
            raise ValueError(f"Dataset alterado: {path.name}")
    data = pd.read_csv(path, dtype={"id": "string", "municipio_id": "string",
                                  "estado_id": "string", "pais_id": "string",
                                  "grupo_validacao": "string", "fold_espacial": "Int64"})
    data["data_hora_gmt"] = pd.to_datetime(data["data_hora_gmt"], utc=True)
    if not data["ano"].eq(ano).all():
        raise ValueError("Arquivo contém registros de outro ano.")
    return data


def iterar_folds(dados, estrategia="espacial"):
    """Gera cinco pares de treino/validação; aceita exclusivamente dados de 2024."""
    if dados.empty or not dados["ano"].eq(2024).all():
        raise ValueError("A validação interna deve usar exclusivamente 2024.")
    if estrategia == "espacial":
        for fold in range(5):
            valid = dados["fold_espacial"].eq(fold)
            yield fold, dados.loc[~valid].copy(), dados.loc[valid].copy()
    elif estrategia == "temporal":
        for fold, start in enumerate((3, 5, 7, 9, 11)):
            yield fold, dados.loc[dados["mes"] < start].copy(), dados.loc[
                dados["mes"].between(start, start + 1)].copy()
    else:
        raise ValueError("Estratégia deve ser 'espacial' ou 'temporal'.")


@dataclass
class Particao:
    X_treino: pd.DataFrame
    X_avaliacao: pd.DataFrame
    y_reg_treino: pd.Series
    y_reg_avaliacao: pd.Series
    y_cls_treino: pd.Series
    y_cls_avaliacao: pd.Series
    limiar_frp: float
    parametros: dict


def preparar_particao(treino, avaliacao, representacao="padronizada"):
    """Imputa pela mediana do treino e oferece números, z-scores ou categorias binárias.

    O percentil 75 e todas as transformações são aprendidos somente em ``treino``.
    A representação discretizada usa a mediana do treino como corte de cada atributo.
    """
    if representacao not in ("numerica", "padronizada", "discretizada"):
        raise ValueError("Representação inválida.")
    if treino.empty or avaliacao.empty:
        raise ValueError("Treino e avaliação não podem ser vazios.")
    if "id" in treino and "id" in avaliacao and set(treino.id) & set(avaliacao.id):
        raise ValueError("Há identificadores compartilhados entre treino e avaliação.")
    if "ano" in treino and not treino.ano.eq(2024).all():
        raise ValueError("O ajuste dos parâmetros deve usar exclusivamente 2024.")
    x_train = treino[ATRIBUTOS].astype(float)
    x_eval = avaliacao[ATRIBUTOS].astype(float)
    if np.isinf(x_train.to_numpy()).any() or np.isinf(x_eval.to_numpy()).any():
        raise ValueError("Atributos contêm infinito; usar o dataset auditado.")
    medians = x_train.median()
    if medians.isna().any():
        raise ValueError("Há atributo inteiramente ausente no treino.")
    x_train, x_eval = x_train.fillna(medians), x_eval.fillna(medians)
    params = {"representacao": representacao, "medianas": medians.to_dict()}
    if representacao == "padronizada":
        means = x_train.mean()
        scales = x_train.std(ddof=0).replace(0, 1)
        x_train, x_eval = (x_train - means) / scales, (x_eval - means) / scales
        params.update({"medias": means.to_dict(), "escalas": scales.to_dict()})
    elif representacao == "discretizada":
        cuts = x_train.median()
        x_train, x_eval = x_train.ge(cuts).astype("int8"), x_eval.ge(cuts).astype("int8")
        params["cortes"] = cuts.to_dict()
    y_train, y_eval = treino["frp"].astype(float), avaliacao["frp"].astype(float)
    if (not np.isfinite(y_train).all() or not np.isfinite(y_eval).all()
            or y_train.lt(0).any() or y_eval.lt(0).any()):
        raise ValueError("FRP deve ser finita e não negativa; o alvo não é imputado.")
    threshold = float(y_train.quantile(0.75, interpolation="linear"))
    return Particao(x_train, x_eval, y_train, y_eval,
                    y_train.ge(threshold).astype("int8"),
                    y_eval.ge(threshold).astype("int8"), threshold, params)
