# 국립한국교통대학교 공지사항 RAG 챗봇
## 📖 프로젝트 개요
이 프로젝트는 국립한국교통대학교의 공지사항을 자동으로 수집, 처리하고, **생성형 AI(GPT-4o)**와 RAG(Retrieval-Augmented Generation) 기술을 활용하여 사용자의 질문에 자연어로 답변하는 지능형 챗봇 시스템입니다.
주요 목표는 다음과 같습니다:

자동화된 정보 수집: Airflow를 사용하여 주기적으로 학교 공지사항(본문, 첨부파일 포함)을 스크래핑합니다.

지식 그래프 및 벡터 DB 구축: 수집된 데이터를 Neo4j 데이터베이스에 벡터 임베딩과 함께 저장하여 의미 기반 검색이 가능하도록 합니다.

지능형 답변 생성: 사용자의 질문 의도를 파악하고, 데이터베이스에서 가장 관련성 높은 정보를 찾아 GPT-4o가 이를 바탕으로 정확하고 신뢰도 높은 답변을 생성합니다.

시스템 성능 평가: Ragas 프레임워크를 통해 구축된 RAG 파이프라인의 성능을 정량적으로 측정하고, 지속적인 개선의 기반을 마련합니다.

### 1. 데이터 파이프라인 (Data Pipeline - Powered by Airflow)
주기적으로 실행되며, 챗봇이 학습할 데이터를 수집하고 가공하여 데이터베이스에 저장합니다.

**스케줄링: Apache Airflow가 매일 정해진 시간에 데이터 수집 프로세스를 자동으로 실행합니다.**

**추출 (Extract): Python, BeautifulSoup, Requests를 사용하여 학교 공지사항 웹 페이지에서 새로운 게시물의 제목, URL, 본문, 첨부파일을 스크래핑합니다.**
**변환 (Transform): hwp5-to-text, pypdf 등을 통해 첨부파일의 내용을 텍스트로 변환하고, 본문과 합쳐 하나의 문서로 만듭니다. 이 문서는 OpenAI Embedding 모델을 통해 고차원 벡터로 변환됩니다.**
**적재 (Load): 원본 텍스트, 메타데이터, 그리고 생성된 벡터 임베딩을 Neo4j 그래프 데이터베이스에 저장합니다.****

### 2. 추론 파이프라인 (Inference Pipeline - Powered by FastAPI & LangChain)

사용자의 요청에 실시간으로 응답하는 챗봇의 핵심 로직입니다.

API 서버: FastAPI를 사용하여 챗봇 API 엔드포인트를 제공합니다.

질문 임베딩: 사용자의 질문을 Embedding 모델을 통해 벡터로 변환합니다.

정보 검색 (Retrieve): Neo4j의 벡터 인덱스를 사용하여 질문 벡터와 가장 유사한 공지사항 문서를 빠르게 검색합니다.

프롬프트 강화 (Augment): 검색된 공지사항 내용(Context)과 사용자의 원본 질문을 미리 정의된 프롬프트 템플릿에 결합합니다.

답변 생성 (Generate): 강화된 프롬프트를 GPT-4o 모델에 전달하여, 주어진 컨텍스트에 기반한 정확하고 자연스러운 답변을 생성합니다.

## 🛠️ 기술 스택

데이터 파이프라인: Apache Airflow, Python, BeautifulSoup, Requests

데이터베이스: Neo4j (Graph & Vector DB), PostgreSQL (Airflow Metadata)

AI / LLM: OpenAI GPT-4o, LangChain, Ragas

백엔드 API: FastAPI, Uvicorn

인프라 / 배포: Docker, Docker Compose

파일 처리: hwp5-to-text, pypdf, python-docx, openpyxl

## ❗ 현재 상태 및 한계점

이 프로젝트는 개념 증명(PoC) 단계이며, 실제 운영을 위해서는 아래와 같은 개선이 필요합니다.

데이터 수집 범위: 현재 Airflow 스케줄러는 "일반소식" 게시판 하나의 정보만을 수집하고 있습니다. "학사공지", "장학안내" 등 다른 주요 게시판의 정보를 포함하도록 스크래핑 로직 확장이 필요합니다.

HWP 파일 처리: 일부 HWP 파일은 DRM(디지털 저작권 관리)으로 보호되어 있어, 현재의 hwp5-to-text 라이브러리로는 내용 추출이 불가능한 경우가 있습니다. 이로 인해 HWP 첨부파일의 정보가 누락될 수 있으며, 이를 해결하기 위한 대체 방안(예: DRM 해제 가능한 솔루션 도입) 모색이 필요합니다.

Graph RAG 미구현: 현재는 벡터 검색 기반의 기본적인 RAG만 구현되어 있습니다. 공지사항의 출처(학과), 키워드, 날짜 등을 노드와 관계로 연결하는 Graph RAG를 도입하면, "작년에 컴퓨터공학과에서 올린 장학금 공지 알려줘"와 같은 복잡한 질문에 더 정확하게 답변할 수 있습니다.

<img width="1202" height="812" alt="image" src="https://github.com/user-attachments/assets/4e18bb78-db71-4c3d-b8da-c5b8601638bc" />
