from langchain_openai import OpenAIEmbeddings
from app.config import settings  # config 폴더의 settings 모듈을 import

embeddings = OpenAIEmbeddings(
    model=settings.EMBEDDING_MODEL,
    openai_api_key=settings.OPENAI_API_KEY
)