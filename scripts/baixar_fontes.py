"""Obtém e verifica os 24 CSVs mensais oficiais do INPE (2024–2025)."""

import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/"
MANIFEST = ROOT / "data/fontes_2024_2025.json"


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def download(url, path):
    partial = path.with_suffix(".csv.part")
    for attempt in range(3):
        try:
            with urlopen(url, timeout=120) as response, partial.open("wb") as dest:
                expected = response.headers.get("Content-Length")
                while block := response.read(1024 * 1024):
                    dest.write(block)
            if expected and partial.stat().st_size != int(expected):
                raise ValueError(f"Download incompleto: {path.name}")
            partial.replace(path)
            return
        except Exception:
            partial.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baixar", action="store_true", help="Baixar arquivos ausentes.")
    parser.add_argument("--registrar-fontes", action="store_true",
                        help="Primeiro registro dos hashes; exige manifesto ainda inexistente.")
    args = parser.parse_args()
    if args.registrar_fontes and MANIFEST.exists():
        raise FileExistsError("O manifesto já existe; não sobrescrever os hashes da fonte.")
    if not MANIFEST.exists() and not args.registrar_fontes:
        raise FileNotFoundError("O manifesto ainda não existe; o primeiro registro precisa ser explícito.")
    previous = {} if args.registrar_fontes else {
        item["arquivo"]: item for item in json.loads(MANIFEST.read_text())["arquivos"]}
    pilot = json.loads((ROOT / "data/manifesto.json").read_text())
    known = {item["arquivo"]: item for item in pilot["arquivos_auditados"]}
    records = []
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    for year in (2024, 2025):
        for month in range(1, 13):
            name = f"focos_mensal_br_{year}{month:02d}.csv"
            path, url = raw / name, BASE + name
            if not path.exists():
                if not args.baixar:
                    raise FileNotFoundError(f"Falta {name}; use --baixar.")
                print(f"Baixando {name}", flush=True)
                download(url, path)
            checksum = sha256(path)
            expected = previous.get(name) or known.get(name)
            if expected and checksum != expected["sha256"]:
                raise ValueError(f"Hash divergente: {name}; reauditar a revisão da fonte.")
            if previous and (name not in previous or previous[name]["url"] != url):
                raise ValueError(f"Manifesto incompatível com a fonte esperada: {name}")
            records.append({"arquivo": name, "url": url, "bytes": path.stat().st_size,
                            "sha256": checksum})
            print(f"Verificado {name}: {path.stat().st_size:,} bytes", flush=True)
    if args.registrar_fontes:
        MANIFEST.write_text(json.dumps({
            "data_acesso": datetime.now(ZoneInfo("America/Manaus")).date().isoformat(),
            "fonte": "INPE — Programa Queimadas", "periodo": [2024, 2025],
            "catalogo": "https://dados.gov.br/dados/conjuntos-dados/monitoramento-de-queimadas",
            "arquivos": records}, ensure_ascii=False, indent=2) + "\n")
    print(f"24 arquivos verificados; total {sum(r['bytes'] for r in records):,} bytes.")


if __name__ == "__main__":
    main()
