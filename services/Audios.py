import os
import json
import requests
import tempfile
import wave
import time

import vosk
from pydantic import BaseModel, HttpUrl
from pydub import AudioSegment
from fastapi import HTTPException

from uuid import uuid4

import pyttsx3

# Caminho do modelo Vosk
VOSK_MODEL_PATH = "models/vosk-model-small-pt-0.3"
if not os.path.exists(VOSK_MODEL_PATH):
    raise RuntimeError("Modelo Vosk não encontrado! Baixe e extraia para a pasta correta.")
model_vosk = vosk.Model(VOSK_MODEL_PATH)

OUTPUT_DIR = 'processed_audios'
os.makedirs(OUTPUT_DIR, exist_ok=True)

class AudioURL(BaseModel):
    arquivo: HttpUrl

class AudioText(BaseModel):
    texto: str
    indice_voz: str = "brazil"
    velocidade: int = 200
    volume: float = 1.0

class Audios:

    @staticmethod
    def voices():
        """
        Lista as vozes disponíveis no sistema com suas informações, como id, nome e idiomas.
        """
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voices_list = []
        for voice in voices:
            # Em alguns sistemas, voice.languages pode vir como bytes, então fazemos a conversão
            langs = [lang.decode("utf-8") if isinstance(lang, bytes) else lang for lang in voice.languages]
            voices_list.append({
                "id": voice.id,
                "name": voice.name,
                "languages": langs,
                "gender": getattr(voice, "gender", None),
                "age": getattr(voice, "age", None)
            })
        return {"voices": voices_list}

    @staticmethod
    def text_to_audio(data: AudioText):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')

            # Encontrar a voz pelo ID (nome) em vez de usar um índice numérico
            voice_found = None
            for voice in voices:
                if voice.id.lower() == data.indice_voz.lower():
                    voice_found = voice
                    break
            
            if not voice_found:
                raise ValueError(f"Voz '{data.indice_voz}' não encontrada. Verifique as vozes disponíveis.")

            engine.setProperty('voice', voice_found.id)
            engine.setProperty('rate', data.velocidade)
            engine.setProperty('volume', data.volume)

            sentences = [s.strip() for s in data.texto.split('.') if s.strip()]
            temp_files = []

            for i, sentence in enumerate(sentences):
                temp_filename = os.path.join(OUTPUT_DIR, f"tmp_{i}_{int(time.time())}.mp3")
                engine.save_to_file(sentence, temp_filename)
                engine.runAndWait()
                temp_files.append(temp_filename)
                time.sleep(0.5)

            combined = AudioSegment.empty()
            for file in temp_files:
                segment = AudioSegment.from_file(file, format="mp3")
                combined += segment

            uuid = uuid4()

            final_filename = os.path.join(OUTPUT_DIR, f"{uuid}.mp3")
            combined.export(final_filename, format="mp3")

            for file in temp_files:
                os.remove(file)

            return {
                "texto": data.texto,
                "indice_voz": voice_found.id,
                "velocidade": data.velocidade,
                "volume": data.volume,
                "audio_processado": f"http://localhost:8000/audios/{uuid}.mp3",
                "extra": {
                    "arquivo": f"{uuid}.mp3",
                    "duracao": combined.duration_seconds,
                    "tamanho": combined.frame_count(),
                    "formato": combined.frame_rate,
                    "model": "pyttsx3",
                }
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao converter texto em áudio: {e}")

    @staticmethod
    def audio_to_text(data: AudioURL):
        """
        Recebe uma URL de áudio (MP3 ou WAV) e retorna a transcrição utilizando o modelo Vosk.
        """
        try:
            # Baixa o áudio da URL
            response = requests.get(data.arquivo)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Erro ao baixar o áudio.")

            # Salva o áudio temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
                temp_audio_file.write(response.content)
                temp_audio_file_path = temp_audio_file.name

            # Converte MP3 para WAV
            audio_wav_path = temp_audio_file_path.replace(".mp3", ".wav")
            audio = AudioSegment.from_file(temp_audio_file_path)
            audio.export(audio_wav_path, format="wav")

            # Processa o áudio WAV com o modelo Vosk
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

            # Junta as transcrições
            transcription = " ".join(res.get("text", "") for res in results).strip()

            # Remove os arquivos temporários
            os.remove(temp_audio_file_path)
            os.remove(audio_wav_path)

            return {
                "transcricao": transcription,
                "extra": {
                    'audio': {
                        'canais': wf.getnchannels(),
                        'amostras_por_segundo': wf.getframerate(),
                        'amostras_por_quadro': wf.getnframes(),
                        'tamanho_quadro': wf.getsampwidth(),
                        'duracao': wf.getnframes() / wf.getframerate(),
                        "formato": wf.getparams()._asdict()
                    },
                    'modelo': "vosk-model-small-pt-0.3"
                }
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao processar o áudio: {e}")
