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


# ============================================================================
# 이 아래는 직접 실행할 때만 동작합니다 (import 시에는 실행 안 됨)
# ============================================================================

if __name__ == "__main__":
    # %% 3. 사용 예시 1: 기본 LLM 사용
    
    print("="*80)
    print("📝 예시 1: 기본 LLM 사용 (단일 호출)")
    print("="*80)
    
    llm = PotensLLM()
    
    # 간단한 질문
    response = llm.invoke("Python으로 리스트를 정렬하는 방법 3가지 알려줘")
    print(f"\n🤖 응답:\n{response}")
    
    # %% 4. 사용 예시 2: Chain과 함께 사용 (LCEL 방식)
    
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    
    print("\n" + "="*80)
    print("⛓️ 예시 2: LCEL Chain 사용 (프롬프트 템플릿)")
    print("="*80)
    
    # 프롬프트 템플릿 정의
    prompt = PromptTemplate(
        input_variables=["language", "task"],
        template="""
당신은 프로그래밍 전문가입니다.

언어: {language}
작업: {task}

위 작업을 수행하는 코드를 작성하고, 간단히 설명해주세요.
"""
    )
    
    # LCEL 방식: | 연산자로 Chain 구성
    chain = prompt | llm | StrOutputParser()
    
    # 실행
    result = chain.invoke({
        "language": "Python",
        "task": "CSV 파일을 읽어서 결측치를 평균값으로 채우기"
    })
    
    print(f"\n🤖 응답:\n{result}")
    
    # %% 5. 사용 예시 3: ChatModel로 멀티턴 대화
    
    print("\n" + "="*80)
    print("💬 예시 3: ChatModel - 멀티턴 대화")
    print("="*80)
    
    chat_model = PotensChatModel()
    
    # 대화 시작
    messages = [
        SystemMessage(content="당신은 데이터 분석 전문가입니다."),
        HumanMessage(content="Pandas에서 groupby를 사용하는 방법을 알려줘")
    ]
    
    response1 = chat_model.invoke(messages)
    print(f"\n🤖 응답 1:\n{response1.content}")
    
    # 대화 이력에 추가
    messages.append(response1)
    messages.append(HumanMessage(content="그럼 여러 컬럼으로 groupby하려면?"))
    
    response2 = chat_model.invoke(messages)
    print(f"\n🤖 응답 2:\n{response2.content}")
    
    # %% 6. 사용 예시 4: Sequential Chain (데이터 분석 파이프라인)
    
    from langchain_core.runnables import RunnablePassthrough
    
    print("\n" + "="*80)
    print("🔄 예시 4: LCEL Sequential Chain - 분석 파이프라인")
    print("="*80)
    
    # Chain 1: 데이터 이해
    understand_prompt = PromptTemplate(
        input_variables=["data_info"],
        template="다음 데이터의 특징을 3줄로 요약해주세요:\n{data_info}"
    )
    
    # Chain 2: 분석 계획
    plan_prompt = PromptTemplate(
        input_variables=["summary"],
        template="""
데이터 요약: {summary}

이 데이터로 할 수 있는 유의미한 분석 3가지를 제안해주세요.
각 분석마다 사용할 Python 라이브러리도 명시해주세요.
"""
    )
    
    # LCEL 방식으로 Sequential Chain 구성
    # Step 1: 데이터 요약
    chain_step1 = understand_prompt | llm | StrOutputParser()
    
    # Step 2: 요약 결과를 받아서 분석 계획 생성
    chain_step2 = (
        {"summary": chain_step1}  # step1의 출력을 summary로 전달
        | plan_prompt 
        | llm 
        | StrOutputParser()
    )
    
    # 실행
    sample_data = """
컬럼: user_id, age, gender, purchase_amount, purchase_date
행 수: 10,000
결측치: age 5%, gender 2%
이상치: purchase_amount에 극단값 존재
"""
    
    print("\n📊 실행 중...")
    summary = chain_step1.invoke({"data_info": sample_data})
    print(f"\n📊 데이터 요약:\n{summary}")
    
    analysis_plan = chain_step2.invoke({"data_info": sample_data})
    print(f"\n📋 분석 계획:\n{analysis_plan}")
    
    # %% 7. 사용 예시 5: Pseudo-Agent (ReAct 패턴)
    
    print("\n" + "="*80)
    print("🤖 예시 5: Pseudo-Agent - ReAct 패턴")
    print("="*80)
    
    class SimplePseudoAgent:
        """
        ReAct 패턴을 사용한 간단한 Pseudo-Agent
        
        Function Calling 없이도 동작하는 Agent
        """
        
        def __init__(self, llm: PotensLLM):
            self.llm = llm
            self.history = []
        
        def run(self, question: str, max_iterations: int = 3):
            """
            질문에 대해 ReAct 패턴으로 답변
            
            Args:
                question: 사용자 질문
                max_iterations: 최대 반복 횟수
            """
            system_prompt = """
당신은 데이터 분석 Agent입니다. 다음 형식으로 답변하세요:

Thought: (무엇을 해야 할지 생각)
Action: python_repl
Action Input: (실행할 Python 코드)

사용자가 "Observation: [결과]"를 제공하면, 그 결과를 분석해서 다음 행동을 결정하세요.
최종 답변을 제공할 준비가 되면 "Final Answer: [답변]" 형식으로 답하세요.
"""
            
            current_prompt = f"사용자 질문: {question}\n\n답변을 시작하세요."
            
            for i in range(max_iterations):
                print(f"\n{'─'*60}")
                print(f"🔄 반복 {i+1}/{max_iterations}")
                print(f"{'─'*60}")
                
                # LLM에게 다음 행동 물어보기
                response = self.llm.invoke(
                    f"{system_prompt}\n\n{current_prompt}",
                )
                
                print(f"\n🤖 LLM 응답:\n{response}")
                
                # Final Answer 확인
                if "Final Answer:" in response:
                    final_answer = response.split("Final Answer:")[1].strip()
                    print(f"\n✅ 최종 답변:\n{final_answer}")
                    return final_answer
                
                # Action Input 추출 (실제로는 정규식 등으로 파싱)
                if "Action Input:" in response:
                    print("\n💡 사용자: (실제로는 여기서 코드를 실행하고 결과를 전달)")
                    print("   예시: Observation: [코드 실행 결과]")
                    
                    # 시뮬레이션: 사용자가 결과를 전달했다고 가정
                    observation = "데이터프레임의 평균값은 42입니다."
                    current_prompt += f"\n\n{response}\n\nObservation: {observation}\n\n다음 행동을 결정하세요."
                else:
                    current_prompt += f"\n\n{response}"
            
            return "최대 반복 횟수 도달"
    
    # Agent 실행
    agent = SimplePseudoAgent(llm=llm)
    result = agent.run("데이터의 평균값을 구하고, 그것이 의미하는 바를 설명해줘")
    
    # %% 8. 교육용 템플릿: Streamlit + Agent 연동 기본 구조
    
    print("\n" + "="*80)
    print("📱 예시 6: Streamlit 연동 기본 구조 (코드 템플릿)")
    print("="*80)
    
    streamlit_template = '''
"""
Streamlit + POTENS Agent 기본 템플릿
실행: streamlit run app.py
"""

import streamlit as st
from potens_wrapper import PotensChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 페이지 설정
st.set_page_config(page_title="나만의 AI 분석 도구", page_icon="🤖")
st.title("🤖 AI 데이터 분석 어시스턴트")

# LLM 초기화
@st.cache_resource
def get_llm():
    return PotensChatModel()

llm = get_llm()

# 세션 상태 초기화 (대화 이력 저장)
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="당신은 데이터 분석 전문가입니다.")
    ]

# 이전 대화 표시
for msg in st.session_state.messages[1:]:  # SystemMessage 제외
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# 사용자 입력
if user_input := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(user_input)
    
    # 메시지 이력에 추가
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    # LLM 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = llm.invoke(st.session_state.messages)
            st.write(response.content)
    
    # 응답도 이력에 추가
    st.session_state.messages.append(response)

# 사이드바: 대화 초기화 버튼
with st.sidebar:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = [
            SystemMessage(content="당신은 데이터 분석 전문가입니다.")
        ]
        st.rerun()
'''
    
    print(streamlit_template)
    
    # %% 9. 다음 단계 가이드
    
    print("\n" + "="*80)
    print("🚀 다음 단계: 교육 과정 구현")
    print("="*80)
    
    print("""
✅ 완료된 것:
  - POTENS API LangChain Wrapper
  - 기본 LLM, ChatModel 구현
  - Chain, Agent 패턴 예시

📚 교육 과정 구현 순서:

1. 2부: LangChain Chain Deep Dive
   ✓ Sequential Chain으로 데이터 분석 파이프라인
   ✓ 이 파일의 예시 4 활용

2. 4부: Streamlit + Agent 연동
   ✓ 이 파일의 예시 6 템플릿 사용
   ✓ CSV 업로드 + 분석 기능 추가

3. 5부: 자율적 EDA Agent
   ✓ Pseudo-Agent 패턴 (예시 5 기반)
   ✓ ReAct 프롬프팅 + 수동 Tool 실행

💡 핵심 포인트:
  - Function Calling 없이도 ReAct 패턴으로 Agent 구현 가능
  - 대화 이력은 messages 배열로 관리
  - Streamlit session_state로 연속성 확보
  
🔧 개선 가능 사항:
  - Tool 실행을 자동화 (safe_exec 구현)
  - 에러 처리 강화
  - 토큰 사용량 모니터링
""")