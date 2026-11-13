import csv
import math
import os
from config import (
    DEFAULT_CSV_PATH,
    ICE_PREVIA_MAX,
    ICE_DULCE_MIN,
    ICE_DULCE_MAX,
)


def determinar_zona(ice: float) -> str:
    if ice is None or math.isnan(ice):
        return "Indeterminado"
    if ice <= ICE_PREVIA_MAX:
        return "Previa a la Dulce"
    if ICE_DULCE_MIN <= ice <= ICE_DULCE_MAX:
        return "Zona Dulce"
    return "Por encima de la Dulce"


def cargar_partidos_csv(ruta_csv: str = DEFAULT_CSV_PATH) -> list[dict]:
    if not os.path.exists(ruta_csv):
        return []
    partidos = []
    seen = set()
    with open(ruta_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clave = (row.get("Fecha"), row.get("Local"), row.get("Visitante"))
            if clave not in seen:
                seen.add(clave)
                partidos.append(row)
    return partidos


def calcular_matriz_pura(partidos: list[dict]) -> list[dict]:
    validos = [p for p in partidos if str(p.get("Gano_Local_Real")) in ("0", "1")]
    if not validos:
        return []

    stats = {}
    for r in validos:
        loc = r["Local"].strip()
        vis = r["Visitante"].strip()
        c_l = float(r.get("Carreras_L", 0))
        c_v = float(r.get("Carreras_V", 0))
        gano_l = int(r["Gano_Local_Real"])

        for eq in (loc, vis):
            if eq not in stats:
                stats[eq] = {"jj": 0, "jg": 0, "cf": 0.0, "cc": 0.0}

        stats[loc]["jj"] += 1
        stats[loc]["jg"] += gano_l
        stats[loc]["cf"] += c_l
        stats[loc]["cc"] += c_v

        stats[vis]["jj"] += 1
        stats[vis]["jg"] += (1 - gano_l)
        stats[vis]["cf"] += c_v
        stats[vis]["cc"] += c_l

    matriz = []
    seen_pairs = set()
    for r in validos:
        loc = r["Local"].strip()
        vis = r["Visitante"].strip()
        if (loc, vis) in seen_pairs:
            continue
        seen_pairs.add((loc, vis))

        sl = stats[loc]
        sv = stats[vis]
        pct_l = sl["jg"] / sl["jj"] if sl["jj"] > 0 else 0.5
        pct_v = sv["jg"] / sv["jj"] if sv["jj"] > 0 else 0.5

        denom = pct_l + pct_v - (2 * pct_l * pct_v)
        prob_l = (pct_l - (pct_l * pct_v)) / denom if denom > 0 else 0.5
        prob_v = 1.0 - prob_l

        ice_vic = round(max(prob_l, prob_v) * 100, 1)
        zona_vic = determinar_zona(ice_vic)

        prom_cf_l = sl["cf"] / sl["jj"]
        prom_cc_l = sl["cc"] / sl["jj"]
        prom_cf_v = sv["cf"] / sv["jj"]
        prom_cc_v = sv["cc"] / sv["jj"]
        total_proj = round(((prom_cf_l + prom_cc_v) / 2.0) + ((prom_cf_v + prom_cc_l) / 2.0), 1)

        ice_altas = round(min(95.0, max(50.0, (total_proj / 220.0) * 70.0)), 1)

        matriz.append({
            "LOCAL": loc,
            "VISITANTE": vis,
            "PROB_LOCAL": round(prob_l * 100, 1),
            "PROB_VISITANTE": round(prob_v * 100, 1),
            "ICE_VICTORIA": ice_vic,
            "ZONA_VICTORIA": zona_vic,
            "TOTAL_PROYECTADO": total_proj,
            "ICE_ALTAS": ice_altas,
        })

    return matriz
