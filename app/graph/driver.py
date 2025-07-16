from neo4j import GraphDatabase
from langchain_community.vectorstores import Neo4jVector
from app.config import settings  # config 폴더의 settings 모듈을 import
from app.rag.embedding import embeddings

# Neo4j 드라이버 인스턴스
try:
    neo4j_driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
    )
    print("Neo4j 드라이버가 성공적으로 생성되었습니다.")
except Exception as e:
    print(f"Neo4j 드라이버 생성 실패: {e}")
    neo4j_driver = None


def get_retriever(search_k: int = 5):
    """
    RAG에 사용할 Neo4jVector Retriever를 생성하는 함수
    """
    if not neo4j_driver:
        raise ConnectionError("Neo4j 드라이버가 초기화되지 않았습니다.")

    try:
        neo4j_vector_store = Neo4jVector.from_existing_index(
            embedding=embeddings,
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD,
            index_name="announcement_embeddings",
            text_node_property="full_text",
            embedding_node_property="embedding",
            retrieval_query="""
            RETURN node.full_text AS text, score, {source: node.url, title: node.title} AS metadata
            """
        )
        print("Neo4j Retriever가 성공적으로 생성되었습니다.")
        return neo4j_vector_store.as_retriever(search_kwargs={'k': search_k})
    except Exception as e:
        print(f"Neo4j Retriever 생성 실패: {e}")
        raise