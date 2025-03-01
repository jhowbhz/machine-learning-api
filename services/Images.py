import os
import time
import uuid
import requests
import cv2
import numpy as np
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl, field_validator
from yolov5 import Yolov5  # Certifique-se de que `Models` está implementado corretamente

# Lista de modelos disponíveis
AVAILABLE_MODELS = ["yolov5s", "yolov5m", "yolov5l", "yolov5x"]

# Diretório para salvar imagens processadas
OUTPUT_DIR = "processed_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ImageURL(BaseModel):
    
    modelo: str
    confianca: float
    arquivo: HttpUrl

    @field_validator("modelo")
    @classmethod
    def check_model(cls, value):
        if value not in AVAILABLE_MODELS:
            raise ValueError(f"Modelo inválido! Escolha entre: {AVAILABLE_MODELS}")
        return value

    @field_validator("confianca")
    @classmethod
    def check_confidence(cls, value):
        if not (0.01 <= value <= 1.0):
            raise ValueError("O valor de confiança deve estar entre 0.01 e 1.0")
        return value

class Images:
    @staticmethod
    def image_to_json(data: ImageURL):
        url = data.arquivo
        modelo = data.modelo
        confianca = max(0.01, min(data.confianca, 1.0))

        try:
            model = Yolov5.load_model(modelo)  # Alterado de Yolov5 para Models
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Erro ao baixar a imagem.")
            contents = response.content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao baixar a imagem: {e}")

        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Não foi possível decodificar a imagem.")

        start_time = time.time()

        results = model(image, size=640)

        inference_time = time.time() - start_time

        detections = results.pandas().xyxy[0]
        detections = detections[detections['confidence'] >= confianca]

        detections_list = detections.to_dict(orient="records")
        confidence_values = detections['confidence'].tolist()
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0

        for det in detections_list:
            x1, y1, x2, y2 = int(det["xmin"]), int(det["ymin"]), int(det["xmax"]), int(det["ymax"])
            label = f"{det['name']} ({det['confidence']:.2f})"
            
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        image_name = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(OUTPUT_DIR, image_name)

        cv2.imwrite(image_path, image)

        return {
            "confianca_utilizada": confianca,
            "tempo_inferencia": round(inference_time, 4),
            "quantidade_itens": len(detections_list),
            "media_confianca": round(avg_confidence, 4),
            "deteccoes": detections_list,
            "extra": {
                "classes_detectadas": list(set(detections['name'].tolist())) if 'name' in detections else [],
                "imagem_original": url,
                "imagem_processada": f"http://localhost:8000/images/{image_name}",
                "modelo": modelo,
            }
        }
