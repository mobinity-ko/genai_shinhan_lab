import os
import requests
from dotenv import load_dotenv
from typing import Any, List, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration

# === 1. 기본 설정 (LLM API 호출 세팅) ===
load_dotenv()
API_KEY = os.getenv("POTENS_API_KEY")

if not API_KEY:
    print("🚨 [에러] .env 파일에서 API Key를 로드하세요.")
else:
    API_URL = "https://ai.potens.ai/api/chat"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    print("✅ (CustomLLM) POTENS API 클라이언트 설정 완료.")

def call_potens_api(prompt, system_prompt=None):
    """POTENS API를 호출하는 헬퍼 함수"""
    body = {"prompt": prompt}
    if system_prompt:
        body["system_prompt"] = system_prompt
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=body, timeout=60)
        response.raise_for_status() # 오류가 있으면 예외 발생
        
        api_response = response.json()
        return api_response.get('message', f'Error: "message" key not found in {api_response}')
    except requests.RequestException as e:
        print(f"🚨 [API 호출 오류] {e}")
        return f"API 호출 중 오류 발생: {e}"


# === 2. LangChain 표준 래퍼(Wrapper) 생성 ===

class PotensChatLLM(BaseChatModel):
    """
    LangChain의 BaseChatModel을 상속받아
    POTENS API를 연동하는 커스텀 LLM 래퍼입니다.
    """
    
    @property
    def _llm_type(self) -> str:
        """LangChain이 모델을 식별하기 위한 필수 속성"""
        return "potens-chat-llm"

    def _format_messages_to_prompts(self, messages: List[BaseMessage]) -> (str, str):
        """
        LangChain의 [BaseMessage] 리스트를
        Potens API가 요구하는 (system_prompt, prompt) 문자열로 변환합니다.
        """
        system_prompt = ""
        chat_history = []

        for msg in messages:
            if isinstance(msg, SystemMessage):
                # 시스템 프롬프트가 여러 개면 연결
                system_prompt = "\n".join([system_prompt, msg.content]).strip()
            elif isinstance(msg, HumanMessage):
                chat_history.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                chat_history.append(f"AI: {msg.content}")
            else:
                chat_history.append(f"Unknown: {msg.content}")
        
        # 마지막 메시지(프롬프트)를 제외한 나머지를 대화 내역으로 합침
        # (참고: API가 대화 내역을 어떻게 처리하는지에 따라 이 부분은 수정이 필요할 수 있습니다)
        # 여기서는 간단히 모든 메시지를 하나의 프롬프트로 합칩니다.
        prompt = "\n".join(chat_history)
        
        return system_prompt, prompt

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Agent가 이 함수를 호출하여 LLM 응답을 요청합니다.
        """
        
        # 1. LangChain 메시지 -> Potens API 포맷으로 변환
        system_prompt, prompt = self._format_messages_to_prompts(messages)
        
        # (디버깅) Agent가 LLM에게 어떤 프롬프트를 보냈는지 확인
        print("\n--- [CustomLLM] Potens API로 전송 ---")
        print(f"[System]: {system_prompt}")
        print(f"[Prompt]: {prompt}")
        print("----------------------------------\n")

        # 2. (핵심) 커스텀 API 헬퍼 함수 호출
        response_text = call_potens_api(prompt, system_prompt)

        # (중요) 디버깅: LangChain Parser가 받기 전의 원본 응답 확인
        print("\n--- [CustomLLM] Potens API의 원본 응답 ---")
        print(response_text)
        print("--------------------------------------\n")
        
        # 3. Potens API 응답(str) -> LangChain 포맷(AIMessage)으로 변환
        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)
        
        return ChatResult(generations=[generation])