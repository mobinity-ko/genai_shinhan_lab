# %% 0. 파일 헤더 및 설명
"""
POTENS API를 LangChain에서 사용하기 위한 Custom Wrapper

사용법:
1. .env에 POTENS_API_KEY 설정
2. PotensLLM 또는 PotensChatModel 사용
3. LangChain의 모든 기능 (Chain, Agent 등)과 호환

예시 실행:
    python potens_wrapper.py  # 예시 코드 실행
    
모듈로 사용:
    from potens_wrapper import PotensLLM, PotensChatModel
"""

import os
import requests
from typing import Any, List, Optional, Dict
from dotenv import load_dotenv

from langchain_core.language_models.llms import LLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun

# %% 1. 기본 LLM Wrapper (간단한 텍스트 입출력)

class PotensLLM(LLM):
    """
    POTENS API를 LangChain LLM으로 래핑
    
    용도: 간단한 텍스트 생성, Chain에서 사용
    """
    
    api_key: str = None
    api_url: str = "https://ai.potens.ai/api/chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_key:
            load_dotenv()
            self.api_key = os.getenv("POTENS_API_KEY")
            if not self.api_key:
                raise ValueError("POTENS_API_KEY를 .env 파일에 설정하거나 api_key 파라미터로 전달하세요.")
    
    @property
    def _llm_type(self) -> str:
        """LLM 타입 식별자"""
        return "potens"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        실제 API 호출 로직
        
        Args:
            prompt: 사용자 입력
            stop: 생성 중지 토큰 (현재 미지원)
            run_manager: LangChain 콜백 매니저
        
        Returns:
            LLM 응답 텍스트
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        body = {"prompt": prompt}
        
        # kwargs에서 system_prompt 추출
        if "system_prompt" in kwargs:
            body["system_prompt"] = kwargs["system_prompt"]
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=body,
                timeout=60
            )
            response.raise_for_status()
            
            api_response = response.json()
            return api_response.get('message', 'Error: No message in response')
            
        except requests.RequestException as e:
            return f"API Error: {str(e)}"


# %% 2. ChatModel Wrapper (대화형, Agent 지원)

class PotensChatModel(BaseChatModel):
    """
    POTENS API를 LangChain ChatModel로 래핑
    
    용도: 
    - 멀티턴 대화
    - Agent 구축 (ReAct 패턴)
    - 대화 이력 관리
    """
    
    api_key: str = None
    api_url: str = "https://ai.potens.ai/api/chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_key:
            load_dotenv()
            self.api_key = os.getenv("POTENS_API_KEY")
            if not self.api_key:
                raise ValueError("POTENS_API_KEY를 .env 파일에 설정하거나 api_key 파라미터로 전달하세요.")
    
    @property
    def _llm_type(self) -> str:
        return "potens_chat"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        메시지 리스트를 받아서 응답 생성
        
        Args:
            messages: [SystemMessage, HumanMessage, AIMessage, ...]
        
        Returns:
            ChatResult with AIMessage
        """
        # 메시지를 POTENS API 형식으로 변환
        prompt, system_prompt = self._messages_to_prompt(messages)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        body = {"prompt": prompt}
        if system_prompt:
            body["system_prompt"] = system_prompt
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=body,
                timeout=60
            )
            response.raise_for_status()
            
            api_response = response.json()
            content = api_response.get('message', 'Error: No message in response')
            
            # ChatGeneration 객체 생성
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
            
        except requests.RequestException as e:
            error_message = AIMessage(content=f"API Error: {str(e)}")
            generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[generation])
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> tuple[str, Optional[str]]:
        """
        LangChain 메시지를 POTENS API 형식으로 변환
        
        Returns:
            (prompt, system_prompt)
        """
        system_prompt = None
        conversation = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_prompt = msg.content
            elif isinstance(msg, HumanMessage):
                conversation.append(f"사용자: {msg.content}")
            elif isinstance(msg, AIMessage):
                conversation.append(f"AI: {msg.content}")
        
        # 대화 이력을 하나의 프롬프트로 결합
        prompt = "\n".join(conversation)
        
        return prompt, system_prompt