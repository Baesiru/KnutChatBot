METRIC_DESCRIPTIONS = {
    "faithfulness": "답변이 제공된 컨텍스트(검색된 공지 내용)에 얼마나 충실하게 근거하는지를 측정합니다. (환각 현상 방지 지표)",
    "answer_relevancy": "생성된 답변이 사용자의 질문과 얼마나 관련이 있는지를 측정합니다.",
    "context_precision": "검색된 컨텍스트 중에서 답변 생성에 실제로 사용된 유용한 정보의 비율을 측정합니다.",
    "context_recall": "정답을 생성하기 위해 필요한 모든 관련 정보가 컨텍스트에 포함되었는지를 측정합니다.",
    "answer_correctness": "생성된 답변이 정답(ground truth)과 얼마나 의미적으로 유사하고 정확한지를 측정합니다.",
}

METRIC_DISPLAY_NAMES = {
    "faithfulness": "충실성 (Faithfulness)",
    "answer_relevancy": "답변 관련성 (Answer Relevancy)",
    "context_precision": "컨텍스트 정확도 (Context Precision)",
    "context_recall": "컨텍스트 재현율 (Context Recall)",
    "answer_correctness": "답변 정확성 (Answer Correctness)",
}