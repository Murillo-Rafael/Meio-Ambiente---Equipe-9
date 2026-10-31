"""ID3 para atributos categóricos numéricos já preparados, sem pré-poda por ganho."""

import numpy as np


def _classes(y):
    y = np.asarray(y)
    if y.ndim != 1 or not np.isin(y, [0, 1]).all():
        raise ValueError("y deve ser um vetor de classes 0/1.")
    return y.astype(int)


def entropia(y):
    """Retorna a entropia binária em bits; conjunto vazio tem entropia zero."""
    y = _classes(y)
    if y.size == 0:
        return 0.0
    proporcoes = np.bincount(y, minlength=2) / y.size
    positivas = proporcoes[proporcoes > 0]
    return float(-np.sum(positivas * np.log2(positivas)))


def ganho_informacao(atributo, y):
    """Entropia do pai menos a entropia ponderada dos filhos por categoria."""
    atributo, y = np.asarray(atributo, dtype=float), _classes(y)
    if atributo.ndim != 1 or atributo.size != y.size or not np.isfinite(atributo).all():
        raise ValueError("Atributo deve ser um vetor finito com o mesmo tamanho de y.")
    if y.size == 0:
        return 0.0
    ponderada = 0.0
    for valor in np.unique(atributo):
        grupo = y[atributo == valor]
        ponderada += grupo.size / y.size * entropia(grupo)
    return float(entropia(y) - ponderada)


def aprender_arvore(X, y, profundidade_maxima=None):
    """Ajusta ID3. Raiz na profundidade 0; empates seguem classe 0 e ordem de X."""
    X, y = np.asarray(X, dtype=float), _classes(y)
    if X.ndim != 2 or len(X) != len(y) or not len(y) or not np.isfinite(X).all():
        raise ValueError("X deve ser uma matriz finita, não vazia e alinhada com y.")
    if profundidade_maxima is not None and (
        not isinstance(profundidade_maxima, (int, np.integer)) or profundidade_maxima < 0
    ):
        raise ValueError("Profundidade máxima deve ser inteira não negativa ou None.")

    def construir(linhas, atributos, profundidade):
        classes = y[linhas]
        contagens = np.bincount(classes, minlength=2)
        no = {"n": len(linhas), "contagens": contagens.tolist(),
              "classe": int(np.argmax(contagens)), "folha": True,
              "n_atributos": X.shape[1]}
        if (contagens == 0).any():
            no["motivo"] = "classes puras"
        elif not atributos:
            no["motivo"] = "atributos esgotados"
        elif profundidade_maxima is not None and profundidade >= profundidade_maxima:
            no["motivo"] = "profundidade máxima"
        else:
            ganhos = [ganho_informacao(X[linhas, j], classes) for j in atributos]
            escolhido = int(np.argmax(ganhos))
            atributo = atributos[escolhido]
            restantes = [j for j in atributos if j != atributo]
            no.update(folha=False, atributo=atributo, ganho=ganhos[escolhido], filhos={})
            for valor in np.unique(X[linhas, atributo]):
                grupo = linhas[X[linhas, atributo] == valor]
                no["filhos"][float(valor)] = construir(grupo, restantes, profundidade + 1)
        return no

    return construir(np.arange(len(y)), list(range(X.shape[1])), 0)


def predizer(arvore, X):
    """Prevê classes; categoria não vista recebe a maioria do nó atual."""
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != arvore["n_atributos"] or not np.isfinite(X).all():
        raise ValueError("X deve ser finito e ter o mesmo número de atributos do treino.")
    previsoes = []
    for linha in X:
        no = arvore
        while not no["folha"]:
            filho = no["filhos"].get(linha[no["atributo"]])
            if filho is None:
                break
            no = filho
        previsoes.append(no["classe"])
    return np.asarray(previsoes, dtype=int)
