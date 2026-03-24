import json
from collections import defaultdict


def analizar_json(data, parent_key=""):
    resultado = []
    valores_por_campo = defaultdict(set)  # Para almacenar valores únicos por campo

    def extraer_valores(data, parent_key=""):
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, (dict, list)):
                    extraer_valores(value, full_key)
                else:
                    if value is not None:
                        valores_por_campo[full_key].add(str(value))
        elif isinstance(data, list):
            for item in data:
                extraer_valores(item, parent_key)

    def construir_estructura(data, parent_key=""):
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    resultado.append({"campo": full_key, "tipo": "object"})
                    construir_estructura(value, full_key)
                elif isinstance(value, list):
                    resultado.append({"campo": full_key, "tipo": "array"})
                    if len(value) > 0:
                        construir_estructura(value[0], full_key)
                else:
                    entry = {"campo": full_key, "tipo": type(value).__name__}

                    # Agregar valores si hay más de uno para este campo
                    if full_key in valores_por_campo and len(valores_por_campo[full_key]) > 1:
                        entry["values"] = sorted(list(valores_por_campo[full_key]))
                    elif full_key in valores_por_campo and len(valores_por_campo[full_key]) == 1:
                        entry["value"] = next(iter(valores_por_campo[full_key]))

                    resultado.append(entry)
        elif isinstance(data, list) and len(data) > 0:
            construir_estructura(data[0], parent_key)

    # Primero, extraer todos los valores
    extraer_valores(data)

    # Luego, construir la estructura con los valores agrupados
    construir_estructura(data, parent_key)

    return resultado


if __name__ == "__main__":
    with open('../jsonExample/netsuite.json', 'r', encoding='utf-8') as archivo:
        datos_netsuite = json.load(archivo)

    with open('../jsonExample/unifier.json', 'r', encoding='utf-8') as archivo:
        datos_unifier = json.load(archivo)

    estructura_netsuite = analizar_json(datos_netsuite)
    estructura_unifier = analizar_json(datos_unifier)

    print("=== ESTRUCTURA NETSUITE ===")
    for campo in estructura_netsuite:
        print(campo)

    print("\n=== ESTRUCTURA UNIFIER ===")
    for campo in estructura_unifier:
        print(campo)