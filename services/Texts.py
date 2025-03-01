from pydantic import BaseModel

from transformers import pipeline

class TextString(BaseModel):
    text: str

class Texts:

    @staticmethod
    def text_to_feelings(data: TextString):

        sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/xlm-roberta-base-sentiment-multilingual", framework="pt")
        result = sentiment_pipeline(data.text)

        return {
            "sentimento": result[0]["label"],
            "confianca": result[0]["score"],
            "extra": {
                'texto': data.text,
                'score': result[0]["score"],
                'rotulo': result[0]["label"],
                'modelo': "cardiffnlp/xlm-roberta-base-sentiment-multilingual"
            }
        }