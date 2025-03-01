import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Importação dos serviços
from services.Images import Images, ImageURL
from services.Audios import Audios, AudioURL, AudioText
from services.Texts import Texts, TextString, OCRInput

# Carregar variáveis de ambiente
load_dotenv()

# Inicialização do FastAPI
app = FastAPI(
    title="API Cassandra - Assistente de IA",
    description=(
        "Essa API é capaz de detectar sentimentos em textos, identificar objetos em imagens, "
        "converter texto em áudio, áudio em texto e imagem em texto."
    ),
    version="0.0.5"
)

# Criar diretórios para arquivos processados, se não existirem
os.makedirs("processed_images", exist_ok=True)
os.makedirs("processed_audios", exist_ok=True)

# Endpoints
@app.post("/image-to-text")
async def image_to_text(data: OCRInput):
    return Texts.image_to_text(data)

@app.get("/audio/voices")
async def audio_voices():
    return Audios.voices()

@app.post("/audio-to-text")
async def audio_to_text(data: AudioURL):
    return Audios.audio_to_text(data)

@app.post("/text-to-audio")
async def text_to_audio(data: AudioText):
    return Audios.text_to_audio(data)

@app.post("/text-to-feelings")
async def text_to_feelings(data: TextString):
    return Texts.text_to_feelings(data)

@app.post("/image-to-json")
async def image_to_json(data: ImageURL):
    return Images.image_to_json(data)

# Servindo arquivos estáticos
app.mount("/images", StaticFiles(directory="processed_images"), name="static-images")
app.mount("/audios", StaticFiles(directory="processed_audios"), name="static-audios")

# Execução do servidor
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 8000))
    )
