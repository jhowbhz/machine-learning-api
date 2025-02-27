from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, field_validator
import requests
import cv2
import numpy as np
import torch
import uvicorn
import time
import os
import uuid
import json
import tempfile  # Corrigido: importando o módulo tempfile corretamente

import wave

import vosk
import torchaudio
from glob import glob
import requests

from pydub import AudioSegment

app = FastAPI(
    title="API de Detecção de Itens",
    description="Recebe uma URL de imagem e retorna os itens detectados utilizando YOLOv5",
    version="1.4"
)

device = torch.device('cpu')  # GPU também funciona, mas os modelos são rápidos o suficiente para CPU

# Diretório onde as imagens processadas serão salvas
OUTPUT_DIR = "processed_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Modelos disponíveis no YOLOv5
AVAILABLE_MODELS = ["yolov5s", "yolov5m", "yolov5l", "yolov5x"]

VOSK_MODEL_PATH = "./models/vosk-model-small-pt-0.3"  # Substitua pelo caminho correto

# Carregar o modelo do Vosk
if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"Modelo Vosk não encontrado em {VOSK_MODEL_PATH}")
model = vosk.Model(VOSK_MODEL_PATH)

# Cache para armazenar os modelos carregados dinamicamente
model_cache = {}

def load_model(model_name: str):
    """Carrega o modelo YOLOv5 especificado e armazena no cache para reuso."""
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Modelo inválido! Escolha entre: {AVAILABLE_MODELS}")
    
    if model_name not in model_cache:
        print(f"Carregando modelo {model_name}...")
        model_cache[model_name] = torch.hub.load('ultralytics/yolov5', model_name, pretrained=True)
    
    return model_cache[model_name]

# Define o schema de entrada com validações
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

# Endpoint para conversão de áudio para texto
class AudioURL(BaseModel):
    arquivo: HttpUrl

@app.post("/audio-to-text")
async def audio_to_text(data: AudioURL):
    """
    Endpoint que recebe uma URL de áudio (MP3 ou WAV) e retorna a transcrição utilizando o modelo Vosk.
    """
    try:
        # Baixa o arquivo de áudio
        response = requests.get(data.arquivo)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Erro ao baixar o áudio.")
        audio_data = response.content

        # Salva o arquivo de áudio temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
            temp_audio_file.write(audio_data)
            audio_file_path = temp_audio_file.name

        # Se o arquivo for MP3, converte para WAV usando Pydub
        if audio_file_path.endswith('.mp3'):
            # Usando Pydub para garantir que a conversão seja feita corretamente
            wav_file_path = audio_file_path.replace('.mp3', '.wav')
            audio = AudioSegment.from_mp3(audio_file_path)
            audio.export(wav_file_path, format="wav")  # Converte para WAV
            os.remove(audio_file_path)  # Deleta o MP3
            audio_file_path = wav_file_path

        # Agora que temos o arquivo WAV, vamos processá-lo com Vosk
        with wave.open(audio_file_path, "rb") as wf:
            rec = vosk.KaldiRecognizer(model, wf.getframerate())
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    results.append(rec.Result())
            results.append(rec.FinalResult())

        # Concatena as transcrições
        transcription = ''.join(results)
        transcription_json = json.loads(transcription)

        # Remove o arquivo temporário
        os.remove(audio_file_path)

        return {"transcricao": transcription_json.get('text', '')}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar o áudio: {e}")

@app.post("/detect")
async def detect_items(data: ImageURL):
    """
    Endpoint que recebe uma URL de imagem via JSON e retorna os itens detectados com mais detalhes, incluindo a imagem processada.
    """
    url = data.arquivo
    modelo = data.modelo
    confianca = max(0.01, min(data.confianca, 1.0))

    try:
        model = load_model(modelo)
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

    # Marca o tempo inicial
    start_time = time.time()

    # Faz a inferência
    results = model(image, size=640)

    # Calcula o tempo de inferência
    inference_time = time.time() - start_time

    # Obtém os detalhes das detecções
    detections = results.pandas().xyxy[0]
    detections = detections[detections['confidence'] >= confianca]

    # Adiciona mais detalhes às detecções
    detections_list = detections.to_dict(orient="records")
    confidence_values = detections['confidence'].tolist()
    avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0

    # Desenha as detecções na imagem
    for det in detections_list:
        x1, y1, x2, y2 = int(det["xmin"]), int(det["ymin"]), int(det["xmax"]), int(det["ymax"])
        label = f"{det['name']} ({det['confidence']:.2f})"
        
        # Desenha a caixa e o rótulo
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Salva a imagem processada com um nome único
    image_name = f"{uuid.uuid4()}.jpg"
    image_path = os.path.join(OUTPUT_DIR, image_name)
    cv2.imwrite(image_path, image)

    return {
        "imagem": {
            "url": url,
            "largura": image.shape[1],
            "altura": image.shape[0],
            "canais": image.shape[2],
        },
        "modelo_utilizado": modelo,
        "confianca_utilizada": confianca,
        "quantidade_itens": len(detections_list),
        "tempo_inferencia": round(inference_time, 4),  # Tempo em segundos
        "dimensoes_imagem": results.ims[0].shape[:2],  # (altura, largura)
        "media_confianca": round(avg_confidence, 4),  # Confiança média das detecções
        "classes_detectadas": list(set(detections['name'].tolist())) if 'name' in detections else [],
        "detections": detections_list,
        "imagem_processada": f"http://localhost:8000/static/{image_name}"  # URL para acessar a imagem
    }

# Rota para servir as imagens processadas
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=OUTPUT_DIR), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
