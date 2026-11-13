import csv
from config import DEFAULT_OUTPUT_PATH


def filtrar_por_zona(matriz: list[dict], zona_objetivo: str) -> list[dict]:
    if not matriz:
        return []
    objetivo = zona_objetivo.strip().lower()
    return [
        fila for fila in matriz
        if str(fila.get("ZONA_VICTORIA", "")).strip().lower() == objetivo
    ]


def generar_resumen_texto(matriz: list[dict]) -> str:
    if not matriz:
        return "No hay enfrentamientos disponibles para mostrar."

    lineas = ["=== RESUMEN DE PROYECCIONES NBA ==="]
    for item in matriz:
        linea = (
            f"{item['LOCAL']} vs {item['VISITANTE']} | "
            f"Prob: {item['PROB_LOCAL']}% - {item['PROB_VISITANTE']}% | "
            f"ICE: {item['ICE_VICTORIA']} ({item['ZONA_VICTORIA']}) | "
            f"Total Proj: {item['TOTAL_PROYECTADO']}"
        )
        lineas.append(linea)
    return "\n".join(lineas)


def exportar_matriz_csv(matriz: list[dict], ruta_salida: str = DEFAULT_OUTPUT_PATH) -> str:
    if not matriz:
        return ""

    campos = list(matriz[0].keys())
    with open(ruta_salida, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(matriz)
    return ruta_salida
