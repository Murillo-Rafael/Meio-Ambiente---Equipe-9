"""Etapa 3: probabilidade sobre variáveis binárias, implementada com NumPy.

Uma distribuição conjunta de ``k`` variáveis binárias é um array de formato
``(2,) * k``: o eixo ``i`` pertence à variável ``i`` e o valor do índice é 0 ou 1.
As frequências relativas são estimativas; os cortes que definem cada variável
devem ser aprendidos no treino, antes de chamar estas funções.
"""

import math

import numpy as np


def binarizar(valores, corte, estrito=False):
    """Devolve 1 se valor >= corte (ou valor > corte, se ``estrito``) e 0 caso contrário."""
    valores = np.asarray(valores, dtype=float)
    if np.isnan(valores).any():
        raise ValueError("Há ausências; imputar ou remover antes de binarizar.")
    return (valores > corte if estrito else valores >= corte).astype("int8")


def contagens_conjuntas(*variaveis):
    """Conta os 2**k eventos atômicos das variáveis binárias (mesmo comprimento)."""
    if not variaveis:
        raise ValueError("Informe ao menos uma variável.")
    colunas = [np.asarray(v, dtype=int) for v in variaveis]
    if len({len(c) for c in colunas}) != 1 or len(colunas[0]) == 0:
        raise ValueError("As variáveis devem ter o mesmo comprimento, não nulo.")
    if any(not np.isin(c, (0, 1)).all() for c in colunas):
        raise ValueError("Todas as variáveis devem ser binárias (0 ou 1).")
    contagens = np.zeros((2,) * len(colunas), dtype=np.int64)
    np.add.at(contagens, tuple(colunas), 1)
    return contagens


def conjunta(*variaveis):
    """Distribuição conjunta empírica: contagens / N, somando 1."""
    contagens = contagens_conjuntas(*variaveis)
    return contagens / contagens.sum()


def marginal(conj, manter):
    """Marginaliza a conjunta, mantendo os eixos de ``manter`` nessa ordem."""
    manter = tuple(manter)
    if len(set(manter)) != len(manter) or not set(manter) <= set(range(conj.ndim)):
        raise ValueError("Eixos inválidos ou repetidos.")
    soma = tuple(sorted(set(range(conj.ndim)) - set(manter)))
    resultado = conj.sum(axis=soma) if soma else conj
    ordenados = sorted(manter)
    return np.transpose(resultado, [ordenados.index(eixo) for eixo in manter])


def condicional(conj, alvo, dado):
    """P(alvo | dado). Os eixos do resultado são ``alvo`` seguidos de ``dado``.

    Combinações do condicionante com probabilidade zero produzem NaN.
    """
    alvo, dado = tuple(alvo), tuple(dado)
    if set(alvo) & set(dado):
        raise ValueError("Alvo e condicionante devem ser disjuntos.")
    p_ambos = marginal(conj, alvo + dado)
    p_dado = marginal(conj, dado)
    denominador = p_dado.reshape((1,) * len(alvo) + p_dado.shape)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denominador > 0, p_ambos / denominador, np.nan)


def reconstruir_pela_cadeia(conj, ordem):
    """Regra da cadeia: P(x0) P(x1|x0) P(x2|x0,x1) ..., nos eixos originais de ``conj``.

    Para qualquer ordem dos eixos o produto coincide com a conjunta empírica.
    """
    ordem = tuple(ordem)
    if sorted(ordem) != list(range(conj.ndim)):
        raise ValueError("A ordem deve ser uma permutação de todos os eixos.")
    letras = "abcdefgh"[: conj.ndim]
    termos, indices = [], []
    for posicao, eixo in enumerate(ordem):
        anteriores = ordem[:posicao]
        fator = condicional(conj, (eixo,), anteriores) if anteriores else marginal(conj, (eixo,))
        termos.append(np.nan_to_num(fator))
        indices.append(letras[eixo] + "".join(letras[e] for e in anteriores))
    return np.einsum(",".join(indices) + "->" + letras, *termos)


def bayes(p_e_dado_h, p_h, p_e):
    """Teorema de Bayes: P(H | E) = P(E | H) P(H) / P(E)."""
    if p_e <= 0:
        raise ValueError("P(E) deve ser positiva.")
    return p_e_dado_h * p_h / p_e


def bayes_binario(p_e_dado_h1, p_e_dado_h0, p_h1):
    """P(H=1 | E=1), obtendo P(E) pela probabilidade total sobre H."""
    p_e = p_e_dado_h1 * p_h1 + p_e_dado_h0 * (1 - p_h1)
    return bayes(p_e_dado_h1, p_h1, p_e)


def qui_quadrado_2x2(contagens):
    """Estatística qui-quadrado de independência (sem correção de continuidade) e p-valor, 1 g.l."""
    contagens = np.asarray(contagens, dtype=float)
    if contagens.shape != (2, 2):
        raise ValueError("Esperada tabela 2x2.")
    n = contagens.sum()
    esperado = np.outer(contagens.sum(axis=1), contagens.sum(axis=0)) / n
    if (esperado == 0).any():
        return 0.0, 1.0
    estatistica = float(((contagens - esperado) ** 2 / esperado).sum())
    return estatistica, math.erfc(math.sqrt(estatistica / 2))


def phi(contagens):
    """Coeficiente phi (correlação entre as duas binárias), com sinal; 0 se uma é constante."""
    c = np.asarray(contagens, dtype=float)
    linhas, colunas = c.sum(axis=1), c.sum(axis=0)
    denominador = math.sqrt(linhas.prod() * colunas.prod())
    return 0.0 if denominador == 0 else float((c[0, 0] * c[1, 1] - c[0, 1] * c[1, 0]) / denominador)


def informacao_mutua(conj2):
    """Informação mútua em bits entre duas binárias; vale 0 se e somente se há independência."""
    produto = np.outer(conj2.sum(axis=1), conj2.sum(axis=0))
    mascara = conj2 > 0
    return float((conj2[mascara] * np.log2(conj2[mascara] / produto[mascara])).sum())


def desvio_independencia(conj2):
    """Maior |P(a,b) - P(a)P(b)| entre os quatro eventos atômicos."""
    return float(np.abs(conj2 - np.outer(conj2.sum(axis=1), conj2.sum(axis=0))).max())


def independencia_condicional(a, b, classe):
    """Compara P(a,b | c) com P(a | c) P(b | c) para cada valor de ``classe``.

    Devolve uma lista com um dicionário por classe (n, phi, informação mútua,
    desvio máximo, qui-quadrado e p-valor) e o teste global somando os
    qui-quadrados das classes (g.l. = número de classes testadas).
    """
    a, b, classe = (np.asarray(v, dtype=int) for v in (a, b, classe))
    linhas, soma_chi2, graus = [], 0.0, 0
    for c in (0, 1):
        mascara = classe == c
        if not mascara.any():
            continue
        contagens = contagens_conjuntas(a[mascara], b[mascara])
        estatistica, p_valor = qui_quadrado_2x2(contagens)
        conj2 = contagens / contagens.sum()
        linhas.append({"classe": c, "n": int(mascara.sum()), "phi": phi(contagens),
                       "informacao_mutua_bits": informacao_mutua(conj2),
                       "desvio_maximo": desvio_independencia(conj2),
                       "qui2": estatistica, "p_valor": p_valor})
        soma_chi2 += estatistica
        graus += 1
    # Para 1 ou 2 graus de liberdade a cauda do qui-quadrado tem forma fechada.
    p_global = {1: math.erfc(math.sqrt(soma_chi2 / 2)), 2: math.exp(-soma_chi2 / 2)}[graus]
    return linhas, {"qui2": soma_chi2, "graus_liberdade": graus, "p_valor": p_global}


def diferenca_risco_por_grupo(alvo, exposto, grupos, repeticoes=2000, semente=42):
    """Diferença P(alvo=1 | exposto=1) - P(alvo=1 | exposto=0) com IC por bootstrap de grupos.

    Reamostra grupos inteiros (por exemplo, municípios) com reposição, pois detecções
    do mesmo município não são independentes. O intervalo é percentílico de 95%.
    """
    alvo, exposto = np.asarray(alvo, dtype=int), np.asarray(exposto, dtype=int)
    codigos, indices = np.unique(np.asarray(grupos), return_inverse=True)
    tabela = np.zeros((len(codigos), 4))
    for coluna, (e, y) in enumerate([(1, 1), (1, 0), (0, 1), (0, 0)]):
        np.add.at(tabela[:, coluna], indices[(exposto == e) & (alvo == y)], 1)

    def diferenca(soma):
        n1, n0 = soma[0] + soma[1], soma[2] + soma[3]
        if n1 == 0 or n0 == 0:
            return np.nan
        return soma[0] / n1 - soma[2] / n0

    ponto = diferenca(tabela.sum(axis=0))
    gerador = np.random.default_rng(semente)
    sorteios = gerador.integers(0, len(codigos), size=(repeticoes, len(codigos)))
    amostras = np.array([diferenca(tabela[s].sum(axis=0)) for s in sorteios])
    inferior, superior = np.nanpercentile(amostras, [2.5, 97.5])
    return float(ponto), float(inferior), float(superior)
