import logging
import json
import requests
import pandas as pd
from io import StringIO

import azure.functions as func

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    url = "https://raw.githubusercontent.com/Chris1Areiza/lime/main/final_data.txt"
    experiment_id = req.params.get('experiment_id')
    day = req.params.get('day')
    try:
        # Leer el archivo de texto desde Github
        response = requests.get(url)
        content = response.content.decode('utf-8')
        df = pd.read_csv(StringIO(content), sep='\t')
        # Filtrar los resultados del experimento y día especificados
        results = df.loc[(df['Experiment'] == experiment_id) & (df['Day'] == day)]
        # Si no hay resultados para el experimento y día especificados, devolver error 404
        if results.empty:
            return func.HttpResponse(f"Experimento no encontrado", status_code=404)
        # Crear un diccionario con los resultados
        experiment_data = {}
        variants = []
        for i, row in results.iterrows():
            variant_data = {
                "id": row["Variant"],
                "number_of_purchases": int(row["Buy"])
            }
            variants.append(variant_data)
        experiment_data[experiment_id] = {
            "number_of_participants": int(results["Users"].sum()),
            "winner": str(results["winner_variant"].iloc[0]),
            "variants": variants
        }
        response = json.dumps({"results": experiment_data})
        return func.HttpResponse(response, status_code=200)        
    except Exception as e:
        # Devolver error 500 si ocurre algún error durante la consulta
        func.HttpResponse(str(e),status_code=200)