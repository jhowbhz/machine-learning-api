# Assistente de IA Cassandra - API

<img src="https://github.com/user-attachments/assets/71af7aca-d484-4580-98e5-e0b7609682ec" style="width:100%" alt="Assistente de IA" />
<hr />
<p> Este é um estudo de Machine Learning utilizando alguns modelos específicos de IA, para detecção de objetos em imagens, transcrição de áudio, detecção de sentimento em textos e muito mais... </p>

## Funcionalidades básicas

- **Detecção de Itens em Imagens**: Recebe uma URL de imagem e retorna os itens detectados com informações detalhadas sobre a imagem.
- **Transcrição de Áudio**: Recebe uma URL de áudio (MP3 ou WAV) e retorna a transcrição do conteúdo utilizando o modelo **Vosk**.

## Como usar

### 1. Instalação

Para rodar este projeto localmente, siga os passos abaixo:

#### Pré-requisitos:

- **Python 3.8 ou superior**: O projeto foi desenvolvido com Python 3.8, mas versões superiores também são compatíveis.
- **Dependências**: O projeto depende de algumas bibliotecas que podem ser instaladas via `pip`.

#### Clonando o repositorio

```bash
git clone https://github.com/jhowbhz/machine-learning-api.git machine-learning-api && cd machine-learning-api
```

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

#### Models

https://alphacephei.com/vosk/models
