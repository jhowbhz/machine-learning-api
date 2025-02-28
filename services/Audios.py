import os
import json
import requests
import tempfile
import wave

import vosk
from pydantic import BaseModel, HttpUrl
from pydub import AudioSegment
from fastapi import HTTPException

# Caminho do modelo Vosk
VOSK_MODEL_PATH = "models/vosk-model-small-pt-0.3"
if not os.path.exists(VOSK_MODEL_PATH):
    raise RuntimeError("Modelo Vosk não encontrado! Baixe e extraia para a pasta correta.")
model_vosk = vosk.Model(VOSK_MODEL_PATH)

class AudioURL(BaseModel):
    arquivo: HttpUrl

class Audios:
    @staticmethod
    def audio_to_text(data: AudioURL):
        """
        Recebe uma URL de áudio (MP3 ou WAV) e retorna a transcrição utilizando o modelo Vosk.
        """
        try:
            response = requests.get(data.arquivo)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Erro ao baixar o áudio.")

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
                temp_audio_file.write(response.content)
                temp_audio_file_path = temp_audio_file.name

            # Converter para WAV caso seja MP3
            audio_wav_path = temp_audio_file_path.replace(".mp3", ".wav")
            audio = AudioSegment.from_file(temp_audio_file_path)
            audio.export(audio_wav_path, format="wav")

            with wave.open(audio_wav_path, "rb") as wf:
                rec = vosk.KaldiRecognizer(model_vosk, wf.getframerate())
                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        results.append(json.loads(rec.Result()))

                results.append(json.loads(rec.FinalResult()))

            # Juntar todas as transcrições
            transcription = " ".join(res.get("text", "") for res in results).strip()

            # Remover arquivos temporários
            os.remove(temp_audio_file_path)
            os.remove(audio_wav_path)

            return {"transcricao": transcription}

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao processar o áudio: {e}")
