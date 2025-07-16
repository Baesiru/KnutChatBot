from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from app.config import settings
from app.graph.driver import get_retriever
from app.rag.prompt import vector_rag_prompt


def get_vector_rag_chain():
    """
    Vector 검색 기반의 RAG 체인을 생성하는 함수
    """
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.1, openai_api_key=settings.OPENAI_API_KEY)
    retriever = get_retriever()

    question_answer_chain = create_stuff_documents_chain(llm, vector_rag_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain


# 서버 시작 시 체인을 미리 로드
main_rag_chain = get_vector_rag_chain()