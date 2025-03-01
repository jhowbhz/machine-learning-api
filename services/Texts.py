import os
import requests
from pydantic import BaseModel, HttpUrl
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from transformers import pipeline

from fastapi import HTTPException

class TextString(BaseModel):
    text: str

class OCRInput(BaseModel):
    modelo: str
    arquivo: HttpUrl  # Agora garantimos que é uma URL válida

class Texts:

    @staticmethod
    def download_image(url: str, save_path: str):
        """Faz o download da imagem para um arquivo local."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Lança erro se a requisição falhar

            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            return save_path
        
        except Exception as e:
            raise ValueError(f"Erro ao baixar imagem: {e}")

    @staticmethod
    def image_to_text(data: OCRInput):
        """Baixa a imagem da URL e extrai o texto usando OCR com o modelo especificado no body da requisição."""
        try:
            # Verifica qual modelo de OCR foi fornecido
            modelo = data.modelo
            if modelo not in ["db_resnet50", "db_resnet18", "db_mobilenetv3", "db_efficientdet", "db_inceptionv3"]:
                raise HTTPException(status_code=400, detail="Modelo de OCR inválido")

            # Inicia o modelo OCR com base no modelo especificado
            model = ocr_predictor(modelo)  # Usa o modelo especificado na requisição

            image_path = "/tmp/temp_image.jpg"  # Caminho temporário para salvar a imagem

            # Baixa a imagem da URL fornecida
            Texts.download_image(data.arquivo, image_path)

            # Carrega o documento
            doc = DocumentFile.from_images(image_path)

            # Realiza a previsão de OCR
            result = model(doc)

            # Exporte o resultado como JSON
            json_output = result.export()

            # Remove a imagem temporária após o processamento
            os.remove(image_path)

            return {"status": "sucesso", "resultado": json_output}

        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}

    @staticmethod
    def text_to_feelings(data: TextString):
        """Analisa o sentimento de um texto."""
        try:
            sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/xlm-roberta-base-sentiment-multilingual")
            result = sentiment_pipeline(data.text)

            return {
                "status": "sucesso",
                "sentimento": result[0]["label"],
                "confianca": result[0]["score"],
                "detalhes": {
                    "texto": data.text,
                    "score": result[0]["score"],
                    "rotulo": result[0]["label"],
                    "modelo": "cardiffnlp/xlm-roberta-base-sentiment-multilingual"
                }
            }
        
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}
