# Estudo de Machine Learning - API de Detecção de Itens e Transcrição de Áudio

Este projeto é um estudo de Machine Learning utilizando **YOLOv5** para detecção de objetos em imagens e **Vosk** para transcrição de áudio. 

Essa API foi construída com **FastAPI** e permite realizar tarefas de detecção de objetos e transcrição de áudios em formato MP3 ou WAV.

## Funcionalidades

- **Detecção de Itens em Imagens**: Recebe uma URL de imagem e retorna os itens detectados com informações detalhadas sobre a imagem.
- **Transcrição de Áudio**: Recebe uma URL de áudio (MP3 ou WAV) e retorna a transcrição do conteúdo utilizando o modelo **Vosk**.

## Como Usar

### 1. Instalação

Para rodar este projeto localmente, siga os passos abaixo:

#### Pré-requisitos:

- **Python 3.8 ou superior**: O projeto foi desenvolvido com Python 3.8, mas versões superiores também são compatíveis.
- **Dependências**: O projeto depende de algumas bibliotecas que podem ser instaladas via `pip`.

##### Instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Como rodar
```bash
python3 main.py
```

### 3. Documentação

##### a) /audio-to-text - Transcrição de Áudio
```json
body: {
  "arquivo": "URL_DO_ARQUIVO_DE_AUDIO"
}

response: {
  "transcricao": "Texto transcrito do áudio"
}
```

##### b) /detect - Detecção de Itens em Imagens

```json
body: {
  "modelo": "yolov5s",
  "confianca": 0.5,
  "arquivo": "URL_DA_IMAGEM"
}

response: {
  "imagem": {
    "url": "URL_DA_IMAGEM",
    "largura": 1920,
    "altura": 1080,
    "canais": 3
  },
  "modelo_utilizado": "yolov5s",
  "confianca_utilizada": 0.5,
  "quantidade_itens": 3,
  "tempo_inferencia": 0.234,
  "dimensoes_imagem": [1080, 1920],
  "media_confianca": 0.87,
  "classes_detectadas": ["person", "dog", "cat"],
  "detections": [
    {
      "xmin": 100,
      "ymin": 150,
      "xmax": 300,
      "ymax": 350,
      "name": "person",
      "confidence": 0.92
    },
    {
      "xmin": 400,
      "ymin": 100,
      "xmax": 500,
      "ymax": 200,
      "name": "dog",
      "confidence": 0.85
    }
  ],
  "imagem_processada": "http://localhost:8000/static/unique_image_name.jpg"
}
```

##### c) Host da API
https://localhost:8000