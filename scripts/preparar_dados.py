"""Constrói e audita o dataset; exige fontes locais conferidas pelo manifesto de 24 meses."""

import gzip
import hashlib
import io
import json
import platform
import sys
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils import ATRIBUTOS, iterar_folds, preparar_particao  # noqa: E402

COLUMNS = ["id", "lat", "lon", "data_hora_gmt", "satelite", "municipio", "estado",
           "pais", "municipio_id", "estado_id", "pais_id", "numero_dias_sem_chuva",
           "precipitacao", "risco_fogo", "bioma", "frp"]
NUMERIC = ["lat", "lon", "numero_dias_sem_chuva", "precipitacao", "risco_fogo", "frp"]
OUTPUT = ROOT / "data/dataset"


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_csv(path, frame):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as zipped:
        with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as text:
            frame.to_csv(text, index=False, lineterminator="\n")


def process_source(source):
    path = ROOT / "data/raw" / source["arquivo"]
    if sha256(path) != source["sha256"]:
        raise ValueError(f"Fonte alterada: {path.name}")
    expected_month = path.stem[-6:]
    counts, frames, rejects = Counter(), [], []
    for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, skip_blank_lines=False, chunksize=150_000):
        if list(chunk.columns) != COLUMNS:
            raise ValueError(f"Esquema inesperado em {path.name}: {list(chunk.columns)}")
        counts["lidas"] += len(chunk)
        brazil = chunk.pais.eq("Brasil")
        amazon = brazil & chunk.bioma.eq("Amazônia")
        selected = amazon & chunk.satelite.eq("AQUA_M-T")
        counts["brasil"] += int(brazil.sum())
        counts["amazonia"] += int(amazon.sum())
        counts["aqua_amazonia"] += int(selected.sum())
        frame = chunk.loc[selected].copy()
        if frame.empty:
            continue
        frame["arquivo_origem"] = path.name
        frame["linha_origem"] = frame.index + 2
        frame["sha256_origem"] = source["sha256"]

        def keep(mask, reason):
            nonlocal frame
            rejected = frame.loc[~mask, ["id", "arquivo_origem", "linha_origem"]].copy()
            rejected["motivo"] = reason
            counts[reason] += len(rejected)
            rejects.append(rejected)
            frame = frame.loc[mask].copy()

        keep(frame.id.str.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}"),
             "id_invalido")
        frame["data_hora_gmt"] = pd.to_datetime(frame.data_hora_gmt, format="ISO8601", errors="coerce", utc=True)
        keep(frame.data_hora_gmt.notna(), "data_invalida")
        keep(frame.data_hora_gmt.dt.strftime("%Y%m").eq(expected_month), "fora_do_mes_da_fonte")
        for name in NUMERIC:
            frame[name] = pd.to_numeric(frame[name].str.strip(), errors="coerce")
            frame.loc[~np.isfinite(frame[name]) | frame[name].eq(-999), name] = np.nan
        keep(frame.lat.between(-34, 6) & frame.lon.between(-74, -34), "coordenada_invalida")
        keep(frame.frp.notna() & frame.frp.ge(0), "frp_invalida")
        for name in ("numero_dias_sem_chuva", "precipitacao"):
            frame.loc[frame[name].lt(0), name] = np.nan
        frame.loc[frame.numero_dias_sem_chuva.mod(1).ne(0), "numero_dias_sem_chuva"] = np.nan
        frame.loc[~frame.risco_fogo.between(0, 1), "risco_fogo"] = np.nan
        for name in ("numero_dias_sem_chuva", "precipitacao"):
            frame[name + "_ausente"] = frame[name].isna().astype("int8")
            counts[name + "_ausente"] += int(frame[name].isna().sum())
        counts["risco_fogo_ausente"] += int(frame.risco_fogo.isna().sum())
        frame["ano"] = frame.data_hora_gmt.dt.year
        frame["mes"] = frame.data_hora_gmt.dt.month
        frame["hora_utc"] = (frame.data_hora_gmt.dt.hour + frame.data_hora_gmt.dt.minute / 60
                             + frame.data_hora_gmt.dt.second / 3600)
        frame["particao"] = np.where(frame.ano.eq(2024), "desenvolvimento", "teste")
        valid_municipality = frame.municipio_id.str.fullmatch(r"\d{7}")
        cell = (np.floor(frame.lat / 0.25).astype(int).astype(str) + ":"
                + np.floor(frame.lon / 0.25).astype(int).astype(str))
        frame["grupo_validacao"] = np.where(valid_municipality, "municipio:" + frame.municipio_id,
                                            "celula_025:" + cell)
        counts["grupo_espacial_substituto"] += int((~valid_municipality).sum())
        counts["retidas_antes_deduplicacao"] += len(frame)
        frames.append(frame)
    if not frames:
        raise ValueError(f"Nenhum registro válido no recorte: {path.name}")
    return pd.concat(frames, ignore_index=True), dict(counts), rejects


def main():
    manifest_path = ROOT / "data/fontes_2024_2025.json"
    sources = json.loads(manifest_path.read_text())
    expected = {f"focos_mensal_br_{y}{m:02d}.csv" for y in (2024, 2025) for m in range(1, 13)}
    if len(sources["arquivos"]) != 24 or {s["arquivo"] for s in sources["arquivos"]} != expected:
        raise ValueError("O manifesto deve conter exatamente os 24 meses esperados.")
    frames, records, rejected_frames = [], [], []
    for source in sources["arquivos"]:
        print(f"Processando {source['arquivo']}", flush=True)
        frame, counts, rejected = process_source(source)
        frames.append(frame)
        records.append({"arquivo": source["arquivo"], **counts})
        rejected_frames.extend(rejected)
    data = pd.concat(frames, ignore_index=True).sort_values(
        ["data_hora_gmt", "lat", "lon", "id", "arquivo_origem", "linha_origem"], kind="stable")
    duplicates = {}
    for key, fields in [("id", ["id"]), ("local_horario_sensor", ["lat", "lon", "data_hora_gmt", "satelite"])]:
        all_copies = data.loc[data.duplicated(fields, keep=False)]
        for _, group in all_copies.groupby(fields, dropna=False):
            if group[NUMERIC + ["data_hora_gmt"]].nunique(dropna=False).gt(1).any():
                raise ValueError(f"Duplicata conflitante por {key}; investigar antes de excluir.")
        repeated = data.duplicated(fields, keep="first")
        duplicates[key] = int(repeated.sum())
        rejected = data.loc[repeated, ["id", "arquivo_origem", "linha_origem"]].copy()
        rejected["motivo"] = "duplicata_" + key
        rejected_frames.append(rejected)
        data = data.loc[~repeated].copy()
    data = data.reset_index(drop=True)
    dev_mask = data.ano.eq(2024)
    dev = data.loc[dev_mask].copy()
    data["fold_espacial"] = pd.Series(pd.NA, index=data.index, dtype="Int64")
    for fold, (_, valid) in enumerate(GroupKFold(n_splits=5).split(dev, groups=dev.grupo_validacao)):
        data.loc[dev.index[valid], "fold_espacial"] = fold
    dev = data.loc[dev_mask].copy()
    split_audit = {}
    for strategy in ("espacial", "temporal"):
        rows = []
        for fold, train, valid in iterar_folds(dev, strategy):
            partition = preparar_particao(train, valid)
            if partition.y_cls_treino.nunique() != 2 or partition.y_cls_avaliacao.nunique() != 2:
                raise ValueError(f"Fold {strategy}/{fold} não contém ambas as classes.")
            if strategy == "espacial" and set(train.grupo_validacao) & set(valid.grupo_validacao):
                raise ValueError("Grupo espacial compartilhado.")
            if strategy == "temporal" and train.data_hora_gmt.max() >= valid.data_hora_gmt.min():
                raise ValueError("A validação temporal não está no futuro do treino.")
            rows.append({"fold": fold, "treino": len(train), "validacao": len(valid),
                         "grupos_treino": train.grupo_validacao.nunique(),
                         "grupos_validacao": valid.grupo_validacao.nunique(),
                         "inicio_validacao": valid.data_hora_gmt.min().isoformat(),
                         "fim_validacao": valid.data_hora_gmt.max().isoformat(),
                         "limiar_frp_mw_do_treino": partition.limiar_frp,
                         "positivos_treino": int(partition.y_cls_treino.sum()),
                         "positivos_validacao": int(partition.y_cls_avaliacao.sum()),
                         "imputacao_mediana_treino": partition.parametros["medianas"]})
        split_audit[strategy] = rows
    audit_years, artifacts = {}, {}
    for year, name in ((2024, "desenvolvimento_2024.csv.gz"), (2025, "teste_2025.csv.gz")):
        frame = data.loc[data.ano.eq(year)].copy()
        numeric_summary = frame[ATRIBUTOS].describe().to_dict()
        audit_years[str(year)] = {
            "linhas": len(frame), "grupos": frame.grupo_validacao.nunique(),
            "inicio": frame.data_hora_gmt.min().isoformat(), "fim": frame.data_hora_gmt.max().isoformat(),
            "dias_com_deteccao": frame.data_hora_gmt.dt.date.nunique(),
            "linhas_por_mes": frame.groupby("mes").size().to_dict(),
            "linhas_por_estado": frame.groupby("estado").size().to_dict(),
            "ausencias": frame[NUMERIC].isna().sum().to_dict(),
            "casos_completos_atributos": int(frame[ATRIBUTOS].notna().all(axis=1).sum()),
            "estatisticas_atributos": numeric_summary}
        if year == 2024:
            audit_years[str(year)]["estatisticas_frp"] = frame.frp.describe(percentiles=[.25, .5, .75, .95, .99]).to_dict()
            audit_years[str(year)]["frp_zero"] = int(frame.frp.eq(0).sum())
        frame["data_hora_gmt"] = frame.data_hora_gmt.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        path = OUTPUT / name
        write_csv(path, frame)
        artifacts[name] = {"linhas": len(frame), "bytes": path.stat().st_size, "sha256": sha256(path)}
    exclusions = pd.concat(rejected_frames, ignore_index=True)
    write_csv(OUTPUT / "exclusoes.csv.gz", exclusions)
    counts_by_file = {row["arquivo"]: row for row in records}
    for source in sources["arquivos"]:
        counts_by_file[source["arquivo"]]["retidas_finais"] = int(data.arquivo_origem.eq(source["arquivo"]).sum())
    write_json(OUTPUT / "manifesto.json", {
        "versao": 1, "fonte_manifesto_sha256": sha256(manifest_path), "arquivos": artifacts,
        "filtros": {"pais": "Brasil", "bioma": "Amazônia", "satelite": "AQUA_M-T"},
        "particoes": {"desenvolvimento": 2024, "teste": 2025},
        "construcao": {"python": platform.python_version(),
            "pacotes": {p: version(p) for p in ("numpy", "pandas", "scikit-learn")},
            "codigo_sha256": {"utils.py": sha256(ROOT / "utils.py"),
                               "scripts/preparar_dados.py": sha256(Path(__file__))}},
        "colunas": list(data.columns), "atributos": ATRIBUTOS,
        "alvo_regressao": "frp", "alvo_classificacao": "frp >= percentil 75 do treino corrente",
        "limiar_frp_mw_ajuste_final_2024": float(dev.frp.quantile(.75)),
        "politica_teste": "2025: somente integridade e cobertura; sem métricas ou distribuição de FRP",
        "artefatos_auditoria": {"exclusoes.csv.gz": {"linhas": len(exclusions),
            "sha256": sha256(OUTPUT / "exclusoes.csv.gz")}}})
    write_json(ROOT / "docs/auditoria-dataset.json", {
        "fonte_manifesto_sha256": sha256(manifest_path), "arquivos": records,
        "totais": {k: sum(row.get(k, 0) for row in records) for k in sorted(set().union(*(r.keys() for r in records)) - {"arquivo"})},
        "duplicatas_removidas": duplicates,
        "exclusoes_por_motivo": exclusions.motivo.value_counts().to_dict(),
        "anos": audit_years, "validacao": split_audit,
        "teste_frp_descritiva_omitida": True,
        "criterios": ["24 fontes íntegras", "somente Brasil/Amazônia/AQUA_M-T",
                      "datas compatíveis com o mês da fonte", "FRP válida sem imputação",
                      "ausências de atributos preservadas", "identificadores únicos",
                      "cinco folds espaciais sem compartilhamento de grupo",
                      "cinco folds temporais com treino anterior à validação",
                      "ambas as classes em todos os folds", "parâmetros aprendidos só no treino"]})
    print(f"Dataset construído: {len(dev):,} registros em 2024; {len(data) - len(dev):,} em 2025.")


if __name__ == "__main__":
    main()
