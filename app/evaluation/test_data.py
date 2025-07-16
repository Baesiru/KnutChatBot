import logging
import pandas as pd
from datasets import Dataset
from typing import List

from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context

from app.config import settings
from app.graph.driver import neo4j_driver
from app.rag.embedding import embeddings

logger = logging.getLogger(__name__)


class TestDataGenerator:

    def __init__(self):
        self.generator_llm = ChatOpenAI(model="gpt-4o", openai_api_key=settings.OPENAI_API_KEY)
        self.critic_llm = ChatOpenAI(model="gpt-4", openai_api_key=settings.OPENAI_API_KEY)
        self.testset_generator = TestsetGenerator.from_langchain(
            self.generator_llm,
            self.critic_llm,
            embeddings=embeddings  # <-- embeddings 인자 추가
        )
        logger.info("TestDataGenerator가 초기화되었습니다.")

    def _load_documents_from_neo4j(self, sample_count: int = 50) -> List[Document]:
        """Neo4j에서 샘플 문서를 로드합니다."""
        documents = []
        with neo4j_driver.session() as session:
            # 랜덤하게 문서를 샘플링하여 다양성을 확보
            result = session.run(
                "MATCH (a:Announcement) RETURN a.full_text AS text, a.url AS url, rand() as r ORDER BY r LIMIT $count",
                {"count": sample_count}
            )
            for record in result:
                documents.append(Document(page_content=record["text"], metadata={"source": record["url"]}))
        logger.info(f"Neo4j에서 {len(documents)}개의 문서를 샘플링했습니다.")
        return documents

    def generate(self, doc_sample_count: int = 50, test_size: int = 10) -> Dataset:
        """
        문서를 기반으로 질문/정답 데이터셋을 생성합니다.

        :param doc_sample_count: DB에서 샘플링할 문서의 수
        :param test_size: 생성할 질문/정답 쌍의 수
        :return: Hugging Face Dataset 객체
        """
        documents = self._load_documents_from_neo4j(sample_count=doc_sample_count)
        if not documents:
            raise ValueError("Neo4j에서 문서를 로드할 수 없습니다. DB에 데이터가 있는지 확인하세요.")

        distributions = {simple: 0.5, reasoning: 0.25, multi_context: 0.25}

        logger.info(f"{test_size}개의 테스트셋 생성을 시작합니다...")
        testset = self.testset_generator.generate_with_langchain_docs(documents, test_size=test_size,
                                                                      distributions=distributions)
        logger.info("테스트셋 생성이 완료되었습니다.")

        return testset.to_dataset()

    def save_to_csv(self, dataset: Dataset, filepath: str):
        """데이터셋을 CSV 파일로 저장합니다."""
        df = dataset.to_pandas()
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"테스트 데이터가 '{filepath}'에 저장되었습니다.")

    def load_from_csv(self, filepath: str) -> Dataset:
        """CSV 파일에서 데이터셋을 로드합니다."""
        df = pd.read_csv(filepath)
        return Dataset.from_pandas(df)
