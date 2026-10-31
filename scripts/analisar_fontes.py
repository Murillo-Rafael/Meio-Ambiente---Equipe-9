"""Auditoria descritiva da fonte INPE; não treina modelos. Python >= 3.11, sem dependências."""

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NUMERIC = ("frp", "numero_dias_sem_chuva", "precipitacao", "risco_fogo", "lat", "lon")


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


@contextmanager
def open_csv(path):
    if path.suffix == ".zip":
        with ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.endswith(".csv")]
            if len(names) != 1:
                raise ValueError(f"Esperado um CSV no ZIP: {path}")
            with archive.open(names[0]) as stream:
                with io.TextIOWrapper(stream, encoding="utf-8-sig", newline="") as text:
                    yield text
    else:
        with path.open(encoding="utf-8-sig", newline="") as text:
            yield text


def number(row, key):
    try:
        value = float(row[key])
    except (ValueError, TypeError, KeyError):
        return None
    if not math.isfinite(value) or value == -999:
        return None
    if key in ("frp", "numero_dias_sem_chuva", "precipitacao") and value < 0:
        return None
    if key == "risco_fogo" and not 0 <= value <= 1:
        return None
    if key == "lat" and not -90 <= value <= 90:
        return None
    if key == "lon" and not -180 <= value <= 180:
        return None
    return value


def summary(values):
    if not values:
        return None
    q1, median, q3 = statistics.quantiles(values, n=4, method="inclusive") if len(values) > 1 else values * 3
    return {"n": len(values), "min": min(values), "q25": q1,
            "mediana": median, "q75": q3, "max": max(values),
            "media": statistics.fmean(values)}


def profile(path):
    total = amazon = aqua = duplicates = physical_duplicates = complete = 0
    countries, biomes, satellites, states, months = (Counter() for _ in range(5))
    invalid = Counter()
    values = {key: [] for key in NUMERIC}
    identifiers, physical_keys = set(), set()
    date_min = date_max = None
    # Em 2025 audita-se integridade/cobertura; valores FRP ficam reservados ao teste futuro.
    inspect_frp = "2025" not in path.name
    with open_csv(path) as text:
        reader = csv.DictReader(text)
        columns = reader.fieldnames
        for row in reader:
            total += 1
            countries[row.get("pais", "")] += 1
            biomes[row.get("bioma", "")] += 1
            if row.get("pais") != "Brasil" or row.get("bioma") != "Amazônia":
                continue
            amazon += 1
            satellite = row.get("satelite", "não informado no arquivo")
            satellites[satellite] += 1
            if satellite != "AQUA_M-T":
                continue
            aqua += 1
            timestamp = row["data_hora_gmt"]
            date_min = min(date_min or timestamp, timestamp)
            date_max = max(date_max or timestamp, timestamp)
            states[row["estado"]] += 1
            months[timestamp[:7]] += 1
            identifier = row["id"]
            duplicates += identifier in identifiers
            identifiers.add(identifier)
            key = (row["lat"].strip(), row["lon"].strip(), timestamp, satellite)
            physical_duplicates += key in physical_keys
            physical_keys.add(key)
            parsed = {key: number(row, key) for key in NUMERIC}
            complete += all(parsed[k] is not None for k in NUMERIC if k != "risco_fogo")
            for field, value in parsed.items():
                if value is None:
                    invalid[field] += 1
                elif field != "frp" or inspect_frp:
                    values[field].append(value)
    return {"arquivo": path.name, "sha256": digest(path), "bytes": path.stat().st_size,
            "colunas": columns, "linhas_brasil": total, "paises": dict(countries),
            "linhas_por_bioma": dict(biomes), "linhas_amazonia": amazon,
            "satelites_amazonia": dict(satellites),
            "sensor_verificavel_no_arquivo": "satelite" in columns,
            "aqua_amazonia": {
                "linhas": aqua, "inicio": date_min, "fim": date_max,
                "estados": dict(states), "meses": dict(months),
                "duplicatas_id": duplicates, "duplicatas_local_horario_sensor": physical_duplicates,
                "invalidos_ou_ausentes": {k: invalid[k] for k in NUMERIC},
                "casos_completos_sem_risco_fogo": complete,
                "estatisticas": {k: summary(v) for k, v in values.items()
                                 if k != "frp" or inspect_frp},
                "frp_descritiva_reservada_ao_teste": not inspect_frp}
                if "satelite" in columns else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baixar", action="store_true", help="Baixar somente arquivos ausentes do manifesto.")
    parser.add_argument("--saida", type=Path, default=ROOT / "docs/perfil-dados.json")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "data/manifesto.json").read_text())
    results = []
    for source in manifest["arquivos_auditados"]:
        path = ROOT / "data/raw" / source["arquivo"]
        if not path.exists() and args.baixar:
            path.parent.mkdir(parents=True, exist_ok=True)
            partial = path.with_suffix(path.suffix + ".part")
            print(f"Baixando {path.name}", flush=True)
            with urlopen(source["url"], timeout=120) as response, partial.open("wb") as dest:
                while block := response.read(1024 * 1024):
                    dest.write(block)
            partial.rename(path)
        if not path.exists():
            raise FileNotFoundError(f"Falta {path}; use --baixar.")
        if digest(path) != source["sha256"]:
            raise ValueError(f"Fonte alterada: {path.name}. Não atualizar o manifesto sem auditar.")
        print(f"Auditando {path.name}", flush=True)
        results.append(profile(path))
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps({"data_acesso": manifest["data_acesso"],
                                    "escopo": "auditoria de arquivos integrais selecionados; não é amostra aleatória dos anos",
                                    "arquivos": results}, ensure_ascii=False, indent=2) + "\n")
    print(f"Resultado: {args.saida}")


if __name__ == "__main__":
    main()
