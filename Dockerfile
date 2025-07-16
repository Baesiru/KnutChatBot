# Dockerfile

# 사용할 Airflow 이미지와 파이썬 버전을 명시적으로 지정
ARG AIRFLOW_IMAGE="apache/airflow:2.8.4-python3.9"
FROM ${AIRFLOW_IMAGE}

USER root

# 시스템 라이브러리 설치 시, 'git' 추가
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# 1. requirements.txt를 먼저 설치합니다.
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install --force-reinstall "numpy==1.24.4" "pandas==1.5.3"
