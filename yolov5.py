import torch

# Dicionário para armazenar os modelos carregados em cache
model_cache = {}

device = torch.device('cpu')

# Lista de modelos disponíveis no repositório YOLOv5
AVAILABLE_MODELS = ["yolov5s", "yolov5m", "yolov5l", "yolov5x"]

class Yolov5:

    @staticmethod

    def load_model(model_name: str):
        """Carrega o modelo YOLOv5 especificado e armazena no cache para reuso."""
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Modelo inválido! Escolha entre: {AVAILABLE_MODELS}")
        
        if model_name not in model_cache:
            print(f"Carregando modelo {model_name}...")
            model_cache[model_name] = torch.hub.load('ultralytics/yolov5', model_name, pretrained=True)
        
        return model_cache[model_name]

    @staticmethod
    
    def get_availables():
        """Retorna a lista de modelos disponíveis."""
        return AVAILABLE_MODELS