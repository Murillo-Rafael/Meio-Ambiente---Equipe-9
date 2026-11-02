# Do Simbólico à Incerteza: Pipeline Completo de IA

Trabalho Integrado de **Fundamentos de IA** — Prof. Edjard Mota

Pipeline de aprendizado em 6 etapas, do aprendizado simbólico à lógica fuzzy, aplicado a dados oficiais do domínio **[A PREENCHER: Saúde Pública | Educação | Segurança Pública | Meio Ambiente]**.

> **Pergunta prática do projeto:** [A PREENCHER: ex.: "o aluno vai evadir?", "o município terá surto?"]

---

## Equipe

| Nome | E-mail|
|------|--------|
Matheus Henrique de Oliveira Garcia |matheus.garcia@icomp.ufam.edu.br
Samuel de Sousa Castro | samuel.castro@icomp.ufam.edu.br
Gabriel Gregório dos Santos Vitor | gabriel.vitor@icomp.ufam.edu.br
Murillo Rafael de Alcântara Mota | murillo.alcantara@icomp.ufam.edu.br
Lucas Melo dos Santos | lucas.melo@icomp.ufam.edu.br

--

## O pipeline

| Etapa | Tema | Conteúdo | Notebook |
|:-----:|------|----------|----------|
| 1 | Aprendizado simbólico | Árvore de decisão, entropia, ganho de informação, validação cruzada, monotonicidade | `etapa1.ipynb` |
| 2 | Aprendizado linear | Regressão linear, gradiente descendente, regularização L2, regressão logística | `etapa2.ipynb` |
| 3 | Probabilidade | Distribuição conjunta, condicional, regra da cadeia, Bayes, independência | `etapa3.ipynb` |
| 4 | Aprendizado probabilístico | MLE, MAP, Naive Bayes do zero, EM com variável oculta | `etapa4.ipynb` |
| 5 | Redes bayesianas | DAG, CPTs, d-separação, inferência por enumeração | `etapa5.ipynb` |
| 6 | Lógica fuzzy | Variáveis linguísticas, regras Se-Então, sistema Mamdani | `etapa6.ipynb` |

As probabilidades produzidas na Etapa 5 alimentam o sistema fuzzy da Etapa 6, que gera a **decisão final interpretável**. As decisões da Etapa 1 e as probabilidades da Etapa 4 são reaproveitadas nas etapas 5 e 6.

```
Dados oficiais → Etapa 1 → Etapa 2 → Etapa 3 → Etapa 4 → Etapa 5 → Etapa 6 → Decisão final interpretável
```

---

## Estrutura do repositório

```
.
├── README.md
├── requirements.txt
├── relatorio.tex            # Relatório em LaTeX (6–8 páginas, formato artigo)
├── relatorio.pdf
├── etapa1.ipynb
├── etapa2.ipynb
├── etapa3.ipynb
├── etapa4.ipynb
├── etapa5.ipynb
├── etapa6.ipynb
├── utils.py                 # Carga e pré-processamento dos dados, métricas
├── em.py                    # Naive Bayes, MLE/MAP e algoritmo EM
├── fuzzy.py                 # Sistema de inferência fuzzy (Mamdani)
└── dados/                   # Dados brutos e tratados (ver "Dados")
```

---

## Como reproduzir

Requer Python 3.10+.

```bash
git clone [A PREENCHER: URL do repositório]
cd [A PREENCHER: nome da pasta]

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

jupyter notebook
```

Execute os notebooks na ordem (`etapa1.ipynb` → `etapa6.ipynb`). Todos os experimentos usam `np.random.seed(42)` para garantir reprodutibilidade.

**Dependências principais:** `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `scikit-fuzzy`, `pgmpy`, `jupyter`.

---

## Dados

- **Fonte:** [A PREENCHER: portal, ex.: https://dadosabertos.saude.gov.br]
- **Base(s):** [A PREENCHER: ex.: SIH/SUS + IBGE]
- **Ano de referência:** [A PREENCHER]
- **Data de acesso:** [A PREENCHER: dd/mm/aaaa]
- **Variável-alvo:** [A PREENCHER]
- **Atributos utilizados:** [A PREENCHER: 4–6 atributos interpretáveis]

Como baixar e preparar os dados: [A PREENCHER: instruções ou script em `utils.py`].

---

## Etapa 4 — Aprendizado probabilístico e EM

**Objetivo:** aprender parâmetros probabilísticos a partir dos dados e lidar com variável oculta por meio do algoritmo EM.

**O que foi implementado** (`etapa4.ipynb` e `em.py`):

1. **MLE** do parâmetro θ de uma Bernoulli.
2. **MAP** com prior Beta (ex.: Beta[2,2]).
3. **Naive Bayes do zero**, treinado e testado na mesma classificação da Etapa 1.
4. **EM** com variável oculta Z (2 ou 3 componentes).
5. Gráfico da **log-verossimilhança** ao longo das iterações.
6. Comparação **Naive Bayes puro vs. Naive Bayes com EM**.

**Resultados** (validação cruzada 5-fold):

| Modelo | Acurácia |
|--------|:--------:|
| Naive Bayes puro | [A PREENCHER] |
| Naive Bayes + EM | [A PREENCHER] |

- Iterações até a convergência do EM: [A PREENCHER]
- Número de componentes de Z: [A PREENCHER]
- Discussão: [A PREENCHER: o EM melhorou o resultado? Por quê?]

---

## Resultados por etapa

| Etapa | Métrica principal | Resultado |
|:-----:|-------------------|-----------|
| 1 | Acurácia (5-fold) | [A PREENCHER] |
| 2 | R² / Acurácia (logística) | [A PREENCHER] |
| 3 | — | [A PREENCHER] |
| 4 | Acurácia (5-fold) | [A PREENCHER] |
| 5 | Inferência (enumeração vs. pgmpy) | [A PREENCHER] |
| 6 | Decisão fuzzy vs. threshold 0,5 | [A PREENCHER] |

---

## Uso de IA generativa

Foram utilizados assistentes de IA como apoio para geração de código e revisão. Todo o código foi lido, compreendido e validado pela equipe, e os prompts utilizados estão documentados no apêndice do relatório.

---

## Referências

- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach*. 4ª ed., Pearson, 2020. (Caps. 18–20)
- Zadeh, L. A. Fuzzy sets. *Information and Control*, 8(3), 338–353, 1965.
- Hüllermeier, E. Fuzzy machine learning and data mining. *WIREs DMKD*, 1(4), 269–283, 2011.
- Portal de dados abertos: https://dados.gov.br
