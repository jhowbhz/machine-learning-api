import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from services.Images import Images, ImageURL
from services.Audios import Audios, AudioURL
from services.Texts import Texts, TextString

app = FastAPI(
    title="API Cassandra - Assistente de IA",
    description="Essa API é capaz de detectar sentimentos em textos, transcrever áudios e identificar objetos em imagens.",
    version="1.4"
)

@app.post("/text-to-feelings")
async def text_to_feelings(data: TextString):
    return Texts.text_to_feelings(data)

@app.post("/audio-to-text")
async def audio_to_text(data: AudioURL):
    return Audios.audio_to_text(data)

@app.post("/image-to-json")
async def image_to_json(data: ImageURL):
    return Images.image_to_json(data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
