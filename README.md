![image](https://github.com/user-attachments/assets/3e4a2609-b5c3-4cc8-bf58-80acd522d555)# API de Detecção de Itens e Transcrição de Áudio
![image](https://github.com/user-attachments/assets/aa7a6acb-4cf6-428c-acad-8d03d4cecf66)

Este é um estudo de Machine Learning utilizando **YOLOv5** para detecção de objetos em imagens e **Vosk** para transcrição de áudio. 

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

body:
```json
{
  "arquivo": "URL_DO_ARQUIVO_DE_AUDIO"
}
```

response:
```json
{
  "transcricao": "Texto transcrito do áudio"
}
```

##### b) /detect - Detecção de Itens em Imagens

body:
```json
{
  "modelo": "yolov5s",
  "confianca": 0.5,
  "arquivo": "URL_DA_IMAGEM"
}
```
response:
```json
{
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

##### Prints
![ffd0b774-2a3c-4994-ad8c-ff939c679659](https://github.com/user-attachments/assets/5d6994e9-f7ea-4a9e-bf4f-82c2ccb39879)

![image](https://github.com/user-attachments/assets/aff341d0-9dab-4ae8-9b9c-5e96a64a7409)
