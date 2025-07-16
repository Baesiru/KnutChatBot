from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging

from app.rag.chain import main_rag_chain
from app.evaluation.test_data import TestDataGenerator
from app.evaluation.evaluator import RagasEvaluator

# --- Pydantic 스키마 정의 ---
class Query(BaseModel):
    question: str


class Source(BaseModel):
    title: str
    url: str


class Answer(BaseModel):
    question: str
    answer: str
    sources: List[Source]


app = FastAPI(
    title="모듈화된 한국교통대학교 챗봇 API",
    version="5.0.0"
)

origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 허용할 출처 목록
    allow_credentials=True,    # 쿠키를 포함한 요청을 허용할지 여부
    allow_methods=["*"],         # 모든 HTTP 메소드 허용 (GET, POST, 등)
    allow_headers=["*"],         # 모든 HTTP 헤더 허용
)

router = APIRouter()
logger = logging.getLogger(__name__)

evaluation_status = {"is_running": False, "result": None}


async def run_evaluation_task():
    """백그라운드에서 전체 평가 파이프라인을 실행하는 함수"""
    global evaluation_status
    if evaluation_status["is_running"]:
        return

    evaluation_status["is_running"] = True
    evaluation_status["result"] = None

    try:
        logger.info("평가 파이프라인 시작...")
        # 1. 테스트 데이터 생성
        data_gen = TestDataGenerator()
        test_dataset = data_gen.generate(doc_sample_count=20, test_size=3)

        # 2. 평가 실행
        evaluator = RagasEvaluator()
        result = await evaluator.run(test_dataset)

        evaluation_status["result"] = result
        logger.info("평가 파이프라인 완료.")

    except Exception as e:
        logger.error(f"평가 중 오류 발생: {e}", exc_info=True)
        evaluation_status["result"] = {"error": str(e)}
    finally:
        evaluation_status["is_running"] = False


@router.post("/evaluate", summary="RAG 시스템 평가 실행")
async def start_evaluation(background_tasks: BackgroundTasks):
    if evaluation_status["is_running"]:
        raise HTTPException(status_code=409, detail="평가가 이미 진행 중입니다.")

    background_tasks.add_task(run_evaluation_task)
    return {"message": "RAG 시스템 평가가 시작되었습니다. 완료까지 몇 분 정도 소요됩니다. /evaluate/status 로 상태를 확인하세요."}


@router.get("/evaluate/status", summary="RAG 시스템 평가 상태 및 결과 확인")
async def get_evaluation_status():
    if evaluation_status["is_running"]:
        return {"status": "running", "message": "평가가 진행 중입니다..."}

    if evaluation_status["result"]:
        # Dataset 객체는 JSON으로 바로 변환 불가하므로, dict로 변환
        result_dict = dict(evaluation_status["result"])
        return {"status": "completed", "result": result_dict}

    return {"status": "idle", "message": "실행된 평가가 없습니다. /evaluate 엔드포인트를 POST로 호출하여 평가를 시작하세요."}

@router.post("/chat", response_model=Answer, summary="챗봇에게 질문하기")
async def ask_question(query: Query):
    try:
        question = query.question
        logger.info(f"수신된 질문: {question}")

        response = await main_rag_chain.ainvoke({"input": question})
        answer_text = response.get("answer", "답변을 생성하는 데 문제가 발생했습니다.")

        source_documents = []
        if "context" in response and response["context"]:
            unique_sources = {}
            for doc in response["context"]:
                url = doc.metadata.get("source")
                if url and url not in unique_sources:
                    unique_sources[url] = {"title": doc.metadata.get("title", "제목 없음"), "url": url}
            source_documents = list(unique_sources.values())

        return Answer(
            question=question,
            answer=answer_text,
            sources=source_documents
        )
    except Exception as e:
        logger.error(f"챗봇 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")




app.include_router(router, prefix="/api/v1", tags=["Chat & Evaluation"])

@app.get("/", summary="서버 상태 확인")
def read_root():
    return {"status": "OK"}