# %% 0. 필요한 모듈 임포트
"""
POTENS Wrapper 사용 예시 모음

실행 방법:
1. potens_wrapper.py와 같은 디렉토리에 위치
2. .env에 POTENS_API_KEY 설정
3. 전체 실행 또는 셀 단위로 실행 (# %% 활용)
"""

from potens_wrapper import PotensLLM, PotensChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough

# %% 1. 사용 예시 1: 기본 LLM 사용

print("="*80)
print("📝 예시 1: 기본 LLM 사용 (단일 호출)")
print("="*80)

llm = PotensLLM()

# 간단한 질문
response = llm.invoke("Python으로 리스트를 정렬하는 방법 3가지 알려줘")
print(f"\n🤖 응답:\n{response}")

# %% 2. 사용 예시 2: Chain과 함께 사용 (LCEL 방식)

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

# %% 3. 사용 예시 3: ChatModel로 멀티턴 대화

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

# %% 4. 사용 예시 4: Sequential Chain (데이터 분석 파이프라인)

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

# %% 5. 사용 예시 5: Pseudo-Agent (ReAct 패턴)

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