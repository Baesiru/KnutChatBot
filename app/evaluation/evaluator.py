import asyncio
import logging
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness, answer_relevancy, context_precision,
    context_recall, answer_correctness
)

from app.rag.chain import main_rag_chain
from app.evaluation.metrics import METRIC_DISPLAY_NAMES, METRIC_DESCRIPTIONS

logger = logging.getLogger(__name__)

try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
except:
    try:
        plt.rcParams['font.family'] = 'NanumGothic'
    except:
        logger.warning("한글 폰트(맑은 고딕, 나눔고딕)를 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
        plt.rcParams['font.family'] = 'monospace'

plt.rcParams['axes.unicode_minus'] = False


class RagasEvaluator:
    """Ragas를 사용하여 RAG 시스템을 평가합니다."""

    def __init__(self):
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness,
        ]
        self.results_dir = os.path.join(os.getcwd(), "evaluation_results")
        os.makedirs(self.results_dir, exist_ok=True)
        logger.info("RagasEvaluator가 초기화되었습니다.")

    async def _collect_responses(self, dataset: Dataset) -> Dataset:
        results = []
        logger.info(f"{len(dataset)}개의 질문에 대한 답변을 수집합니다...")
        for entry in dataset:
            response = await main_rag_chain.ainvoke({"input": entry["question"]})
            results.append({
                "question": entry["question"],
                "answer": response.get("answer", ""),
                "contexts": [doc.page_content for doc in response.get("context", [])],
                "ground_truth": entry["ground_truth"]
            })
        return Dataset.from_list(results)

    async def run(self, test_dataset: Dataset) -> dict:
        logger.info("RAG 시스템 응답 수집을 시작합니다.")
        response_dataset = await self._collect_responses(test_dataset)

        logger.info("Ragas 평가를 시작합니다.")
        score = evaluate(response_dataset, metrics=self.metrics)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df_result = score.to_pandas()
        self._save_results(df_result, timestamp)
        self._visualize_results(df_result, timestamp)

        logger.info("평가가 완료되었습니다.")
        return score

    def _save_results(self, df_result: pd.DataFrame, timestamp: str):
        filepath = os.path.join(self.results_dir, f"evaluation_result_{timestamp}.csv")
        df_result.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"평가 결과가 '{filepath}'에 저장되었습니다.")

    def _visualize_results(self, df_result: pd.DataFrame, timestamp: str):
        scores = df_result.mean()
        metric_names = [METRIC_DISPLAY_NAMES.get(metric, metric) for metric in scores.index]

        plt.figure(figsize=(12, 7))
        bars = sns.barplot(x=metric_names, y=scores.values, palette="viridis")

        plt.title('RAG 시스템 성능 평가 (Ragas)', fontsize=16)
        plt.ylabel('점수 (0.0 ~ 1.0)', fontsize=12)
        plt.ylim(0, 1.05)
        plt.xticks(rotation=45, ha="right")

        for bar in bars.patches:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.01, f'{yval:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        filepath = os.path.join(self.results_dir, f"evaluation_chart_{timestamp}.png")
        plt.savefig(filepath)
        plt.close()
        logger.info(f"평가 결과 차트가 '{filepath}'에 저장되었습니다.")