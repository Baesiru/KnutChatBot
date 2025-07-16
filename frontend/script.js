document.addEventListener('DOMContentLoaded', () => {
    // DOM 요소 가져오기
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');

    const startEvalBtn = document.getElementById('start-evaluation-btn');
    const evaluationStatus = document.getElementById('evaluation-status');
    const evaluationResults = document.getElementById('evaluation-results');

    // API 엔드포인트
    const API_BASE_URL = 'http://localhost:8000/api/v1';
    const CHAT_URL = `${API_BASE_URL}/chat`;
    const EVAL_START_URL = `${API_BASE_URL}/evaluate`;
    const EVAL_STATUS_URL = `${API_BASE_URL}/evaluate/status`;

    let pollingIntervalId = null;

    // 메시지를 채팅창에 추가하는 함수
    function addMessage(text, sender, isLoading = false, sources = []) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);

        if (isLoading) {
            messageElement.classList.add('loading-dots');
            messageElement.innerHTML = '<span></span><span></span><span></span>';
        } else {
            // Sanitize text to prevent HTML injection
            const textNode = document.createElement('div');
            textNode.textContent = text;
            messageElement.appendChild(textNode);

            if (sources.length > 0) {
                const sourcesElement = document.createElement('div');
                sourcesElement.classList.add('sources');
                let sourcesHTML = '<strong>출처:</strong><ul>';
                sources.forEach(source => {
                    sourcesHTML += `<li><a href="${source.url}" target="_blank">${source.title}</a></li>`;
                });
                sourcesHTML += '</ul>';
                sourcesElement.innerHTML = sourcesHTML;
                messageElement.appendChild(sourcesElement);
            }
        }
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight; // 항상 아래로 스크롤
        return messageElement;
    }

    // 챗봇 폼 제출 이벤트 처리
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userMessage = messageInput.value.trim();
        if (!userMessage) return;

        addMessage(userMessage, 'user');
        messageInput.value = '';
        const loadingMessage = addMessage('', 'bot', true);

        try {
            const response = await fetch(CHAT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userMessage }),
            });

            chatWindow.removeChild(loadingMessage); // 로딩 메시지 제거

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '서버에서 오류가 발생했습니다.');
            }

            const data = await response.json();
            addMessage(data.answer, 'bot', false, data.sources);
        } catch (error) {
            console.error('Chat Error:', error);
            addMessage(`오류가 발생했습니다: ${error.message}`, 'bot');
        }
    });

    // 평가 시작 버튼 클릭 이벤트
    startEvalBtn.addEventListener('click', async () => {
        if (pollingIntervalId) {
            alert('평가가 이미 진행 중이거나 완료되었습니다. 새로고침 후 다시 시도하세요.');
            return;
        }

        startEvalBtn.disabled = true;
        evaluationStatus.textContent = '평가 상태: 평가 시작 요청 중...';
        evaluationResults.textContent = '';

        try {
            const response = await fetch(EVAL_START_URL, { method: 'POST' });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '평가 시작에 실패했습니다.');
            }
            const data = await response.json();
            evaluationStatus.textContent = `평가 상태: ${data.message}`;

            // 5초마다 상태 확인 시작
            pollingIntervalId = setInterval(checkEvaluationStatus, 5000);
        } catch (error) {
            console.error('Evaluation Start Error:', error);
            evaluationStatus.textContent = `평가 상태: 오류 - ${error.message}`;
            startEvalBtn.disabled = false;
        }
    });

    // 평가 상태를 주기적으로 확인하는 함수
    async function checkEvaluationStatus() {
        try {
            const response = await fetch(EVAL_STATUS_URL);
            const data = await response.json();

            if (data.status === 'running') {
                evaluationStatus.textContent = '평가 상태: 진행 중...';
            } else if (data.status === 'completed') {
                evaluationStatus.textContent = '평가 상태: 완료';
                evaluationResults.textContent = JSON.stringify(data.result, null, 2);
                clearInterval(pollingIntervalId); // 폴링 중지
                pollingIntervalId = null;
                startEvalBtn.disabled = false; // 버튼 다시 활성화
            } else { // 'idle' 또는 에러
                evaluationStatus.textContent = `평가 상태: ${data.message || '대기 중'}`;
                clearInterval(pollingIntervalId);
                pollingIntervalId = null;
                startEvalBtn.disabled = false;
            }
        } catch (error) {
            console.error('Evaluation Status Error:', error);
            evaluationStatus.textContent = '평가 상태: 상태 확인 중 오류 발생';
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
            startEvalBtn.disabled = false;
        }
    }
});