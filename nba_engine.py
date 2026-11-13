import csv
import math
import os

ICE_PREVIA_MAX = 59.9
ICE_DULCE_MIN = 60.0
ICE_DULCE_MAX = 75.0


def determinar_zona(ice: float) -> str:
    if ice is None or math.isnan(ice):
        return "Indeterminado"
    if ice <= ICE_PREVIA_MAX:
        return "Previa a la Dulce"
    if ICE_DULCE_MIN <= ice <= ICE_DULCE_MAX:
        return "Zona Dulce"
    return "Por encima de la Dulce"


def cargar_partidos_csv(ruta_csv: str) -> list[dict]:
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
        g_l = int(r.get("Gano_Local_Real", 0))

        for eq in (loc, vis):
            if eq not in stats:
                stats[eq] = {"j_tot": 0, "vic": 0, "cf": [], "cc": []}

        stats[loc]["j_tot"] += 1
        stats[loc]["vic"] += g_l
        stats[loc]["cf"].append(c_l)
        stats[loc]["cc"].append(c_v)

        stats[vis]["j_tot"] += 1
        stats[vis]["vic"] += 1 - g_l
        stats[vis]["cf"].append(c_v)
        stats[vis]["cc"].append(c_l)

    matriz = []
    eqs = list(stats.keys())
    for i in range(len(eqs)):
        for j in range(len(eqs)):
            if i == j:
                continue
            loc, vis = eqs[i], eqs[j]
            st_l, st_v = stats[loc], stats[vis]
            n_l, n_v = st_l["j_tot"], st_v["j_tot"]
            if n_l < 2 or n_v < 2:
                continue

            pct_l = st_l["vic"] / n_l
            pct_v = st_v["vic"] / n_v
            denom = pct_l + pct_v - (2 * pct_l * pct_v)
            prob_l = round((pct_l - (pct_l * pct_v)) / denom * 100, 1) if denom != 0 else 50.0

            prom_off_l = sum(st_l["cf"]) / n_l
            prom_def_l = sum(st_l["cc"]) / n_l
            prom_off_v = sum(st_v["cf"]) / n_v
            prom_def_v = sum(st_v["cc"]) / n_v

            varianza_l = sum((x - prom_off_l) ** 2 for x in st_l["cf"]) / (n_l - 1)
            std_l = math.sqrt(varianza_l) if n_l > 1 else 1.0

            exp_tot = round((prom_off_l + prom_def_v) / 2 + (prom_off_v + prom_def_l) / 2, 1)
            factor_m = min(1.0, (n_l + n_v) / 30.0)
            estab = 1.0 / (1.0 + (std_l / (prom_off_l + 0.1)))

            ice_v = round((abs(prob_l - 50.0) * 2 * 0.5) + (factor_m * 25.0) + (estab * 25.0), 1)
            ice_a = round((factor_m * 50.0) + (estab * 50.0), 1)

            matriz.append({
                "LOCAL": loc,
                "VISITANTE": vis,
                "PROB_LOCAL": prob_l,
                "PROB_VISITANTE": round(100.0 - prob_l, 1),
                "ICE_VICTORIA": ice_v,
                "ZONA_VICTORIA": determinar_zona(ice_v),
                "TOTAL_PROYECTADO": exp_tot,
                "ICE_ALTAS": ice_a,
            })
    return matriz
