"""Regressões próprias com NumPy; X não inclui a coluna de intercepto."""

import warnings

import numpy as np


def _com_intercepto(X):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or not np.isfinite(X).all():
        raise ValueError("X deve ser uma matriz finita, sem coluna de intercepto.")
    return np.column_stack([np.ones(len(X)), X])


def _dados_treino(X, y):
    Xb, y = _com_intercepto(X), np.asarray(y, dtype=float)
    if y.ndim != 1 or not len(y) or len(Xb) != len(y) or not np.isfinite(y).all():
        raise ValueError("y deve ser um vetor finito, não vazio e alinhado com X.")
    return Xb, y


def ajustar_univariada(x, y):
    """Retorna [intercepto, inclinação]; x constante usa [média de y, 0]."""
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("x deve ser um vetor unidimensional.")
    _, y = _dados_treino(x[:, None], y)
    centrado = x - x.mean()
    denominador = centrado @ centrado
    inclinacao = centrado @ (y - y.mean()) / denominador if denominador > 0 else 0.0
    return np.array([y.mean() - inclinacao * x.mean(), inclinacao])


def _objetivo_linear(Xb, y, beta, lambda_l2):
    erro = Xb @ beta - y
    penalidade = beta.copy()
    penalidade[0] = 0
    perda = erro @ erro / (2 * len(y)) + lambda_l2 / 2 * (penalidade @ penalidade)
    gradiente = Xb.T @ erro / len(y) + lambda_l2 * penalidade
    return float(perda), gradiente


def _descida(objetivo, n_coeficientes, taxa_aprendizado, max_iter, tolerancia):
    if not np.isfinite(taxa_aprendizado) or taxa_aprendizado <= 0:
        raise ValueError("Taxa de aprendizado deve ser finita e positiva.")
    if not isinstance(max_iter, (int, np.integer)) or max_iter <= 0:
        raise ValueError("max_iter deve ser inteiro positivo.")
    if not np.isfinite(tolerancia) or tolerancia <= 0:
        raise ValueError("Tolerância deve ser finita e positiva.")
    beta, historico = np.zeros(n_coeficientes), []
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        perda, gradiente = objetivo(beta)
        for _ in range(max_iter):
            beta -= taxa_aprendizado * gradiente
            nova_perda, gradiente = objetivo(beta)
            if not np.isfinite(nova_perda) or not np.isfinite(gradiente).all():
                raise FloatingPointError("O ajuste produziu valores não finitos.")
            if nova_perda > perda + 1e-12 * max(1.0, abs(perda)):
                raise FloatingPointError("A perda aumentou; reduza a taxa de aprendizado.")
            historico.append(nova_perda)
            perda = nova_perda
            if np.linalg.norm(gradiente) <= tolerancia:
                break
        else:
            warnings.warn("max_iter atingido antes da tolerância do gradiente.", RuntimeWarning)
    return beta, np.asarray(historico)


def ajustar_linear(X, y, taxa_aprendizado, max_iter, tolerancia, lambda_l2=0.0):
    """Minimiza SSE/(2n) + lambda_l2/2 * ||beta[1:]||² por gradiente.

    Retorna (beta, perdas após cada atualização). Beta começa em zero, o
    intercepto não é penalizado e a parada usa a norma L2 do gradiente.
    """
    Xb, y = _dados_treino(X, y)
    if not np.isfinite(lambda_l2) or lambda_l2 < 0:
        raise ValueError("lambda_l2 deve ser finito e não negativo.")
    return _descida(lambda beta: _objetivo_linear(Xb, y, beta, lambda_l2),
                    Xb.shape[1], taxa_aprendizado, max_iter, tolerancia)


def prever_regressao(X, coeficientes):
    """Retorna estimativas 1D com beta na ordem [intercepto, coef_1, ...]."""
    Xb, beta = _com_intercepto(X), np.asarray(coeficientes, dtype=float)
    if beta.shape != (Xb.shape[1],) or not np.isfinite(beta).all():
        raise ValueError("Coeficientes devem ser finitos e compatíveis com X.")
    return Xb @ beta


def sigmoide(z):
    """Calcula a sigmoide sem exponenciar números positivos grandes."""
    z = np.asarray(z, dtype=float)
    resultado = np.empty_like(z)
    positivos = z >= 0
    resultado[positivos] = 1 / (1 + np.exp(-z[positivos]))
    exponencial = np.exp(z[~positivos])
    resultado[~positivos] = exponencial / (1 + exponencial)
    return resultado


def _objetivo_logistico(Xb, y, beta):
    z = Xb @ beta
    perda = np.mean(np.logaddexp(0, z) - y * z)
    gradiente = Xb.T @ (sigmoide(z) - y) / len(y)
    return float(perda), gradiente


def ajustar_logistica(X, y, taxa_aprendizado, max_iter, tolerancia):
    """Ajusta logística sem penalização; histórico e parada iguais aos da linear."""
    Xb, y = _dados_treino(X, y)
    if not np.isin(y, [0, 1]).all():
        raise ValueError("A logística exige classes 0/1.")
    return _descida(lambda beta: _objetivo_logistico(Xb, y, beta),
                    Xb.shape[1], taxa_aprendizado, max_iter, tolerancia)


def prever_probabilidade(X, coeficientes):
    """Retorna P(classe 1)."""
    return sigmoide(prever_regressao(X, coeficientes))


def prever_classe(X, coeficientes, limiar=0.5):
    """Retorna 1 quando P(classe 1) >= limiar; o limiar não está em MW."""
    if not np.isfinite(limiar) or not 0 <= limiar <= 1:
        raise ValueError("Limiar de probabilidade deve estar entre 0 e 1.")
    return (prever_probabilidade(X, coeficientes) >= limiar).astype(int)
