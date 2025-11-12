"""
핸즈온 랩 2: ReAct 기반 Pandas Pseudo-Agent 구축
소요 시간: 60분
난이도: ⭐⭐⭐

학습 목표:
1. ReAct 프롬프팅 패턴 이해
2. Agent의 "사고 과정" 실시간 관찰 (verbose=True 효과)
3. 사람-AI 협업 패턴 체험
4. Pandas 데이터 분석 자동화
"""

import pandas as pd
import numpy as np
import re
from typing import Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from potens_wrapper import PotensChatModel

# %% [markdown]
# # Part 1: ReAct 패턴 이해하기 (15분)
# 
# ## 🤖 Traditional Agent vs Pseudo-Agent
# 
# ### Traditional Agent (Function Calling 필요)
# ```
# User: "평균 나이 구해줘"
# ↓
# Agent: {"function": "python_repl", "args": {"code": "df['age'].mean()"}}
# ↓ (자동 실행)
# System: 32.5
# ↓ (자동 전달)
# Agent: "평균 나이는 32.5세입니다"
# ```
# 
# ### Pseudo-Agent (ReAct 프롬프팅)
# ```
# User: "평균 나이 구해줘"
# ↓
# Agent: "Thought: 평균을 구해야겠다
#         Action: python_repl
#         Action Input: df['age'].mean()"
# ↓ (👤 사람이 실행)
# User: "Observation: 32.5"
# ↓
# Agent: "평균 나이는 32.5세입니다"
# ```
# 
# **장점:**
# - ✅ Function Calling 불필요
# - ✅ 모든 단계가 투명 (verbose=True 효과)
# - ✅ 사람이 중간 검증 가능
# - ✅ 보안성 향상

# %% 1-1. 샘플 데이터 생성

print("="*80)
print("📊 Part 1: 샘플 데이터 생성")
print("="*80)

# 고객 데이터 생성
np.random.seed(42)
n = 100

df = pd.DataFrame({
    'customer_id': range(1, n+1),
    'name': [f'고객{i}' for i in range(1, n+1)],
    'age': np.random.randint(20, 70, n),
    'gender': np.random.choice(['남', '여'], n),
    'city': np.random.choice(['서울', '경기', '부산', '대구', '기타'], n),
    'purchase_count': np.random.poisson(5, n),
    'total_amount': np.random.exponential(500000, n).astype(int),
    'membership_level': np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'], n, p=[0.4, 0.3, 0.2, 0.1])
})

# 패턴 추가 (인사이트 발굴용)
df.loc[df['membership_level'] == 'Platinum', 'total_amount'] *= 2
df.loc[df['city'] == '서울', 'purchase_count'] += 2

print("\n✅ 샘플 데이터 생성 완료")
print(f"   - 행 수: {len(df)}")
print(f"   - 컬럼: {', '.join(df.columns)}")
print("\n미리보기:")
print(df.head())

# %% [markdown]
# ---
# # Part 2: ReAct 시스템 프롬프트 작성 (10분)

# %% 2-1. ReAct 시스템 프롬프트 정의

PANDAS_AGENT_PROMPT = """
당신은 Pandas 데이터 분석 전문가입니다.

**사용 가능한 데이터프레임:**
- 변수명: df
- 컬럼: {columns}
- 행 수: {num_rows}

**작업 방식:**
사용자의 질문에 답하기 위해 단계별로 생각하고 행동하세요.

**형식 (매우 중요!):**
Thought: (무엇을 해야 할지 생각. 명확하고 구체적으로)
Action: python_repl
Action Input: (실행할 Pandas 코드. 결과를 변수 'result'에 저장)

사용자가 "Observation: [결과]"를 제공하면, 그 결과를 해석하고 다음 행동을 결정하세요.

**최종 답변 시:**
Final Answer: [사용자가 이해할 수 있는 형태로 답변]

**중요 규칙:**
1. 한 번에 하나의 Action만 제안
2. Action Input은 반드시 실행 가능한 완전한 Python 코드
3. 결과는 'result' 변수에 저장 (예: result = df['age'].mean())
4. Observation을 받으면 그 내용을 기반으로 다음 단계 진행
5. 최대 3-5단계 내에 목표 달성

**코드 작성 가이드:**
- df는 이미 로드된 DataFrame
- 간결하고 효율적인 코드 작성
- 에러 가능성 최소화
"""

print("="*80)
print("📝 Part 2: ReAct 시스템 프롬프트 정의")
print("="*80)
print("✅ 프롬프트 정의 완료")

# %% [markdown]
# ---
# # Part 3: Pandas Pseudo-Agent 클래스 구현 (20분)

# %% 3-1. PandasPseudoAgent 클래스

class PandasPseudoAgent:
    """
    ReAct 패턴을 사용하는 Pandas 분석 Agent
    
    verbose=True 처럼 모든 사고 과정을 출력하며,
    사람이 중간에 코드를 검증하고 실행하는 협업 방식
    """
    
    def __init__(self, chat_model: PotensChatModel, df: pd.DataFrame):
        self.chat_model = chat_model
        self.df = df
        self.messages = []
        self.execution_count = 0
        
        # 데이터프레임 정보를 포함한 시스템 프롬프트
        system_prompt = PANDAS_AGENT_PROMPT.format(
            columns=', '.join(df.columns),
            num_rows=len(df)
        )
        self.messages.append(SystemMessage(content=system_prompt))
    
    def run(self, question: str, max_iterations: int = 5, auto_execute: bool = False):
        """
        질문에 대해 ReAct 패턴으로 분석 수행
        
        Args:
            question: 사용자 질문
            max_iterations: 최대 반복 횟수
            auto_execute: True면 자동 실행, False면 사용자 확인
        """
        print("\n" + "="*80)
        print("🤖 Pandas Pseudo-Agent 시작")
        print("="*80)
        print(f"❓ 질문: {question}")
        print(f"🔄 최대 반복: {max_iterations}회")
        print(f"⚙️  실행 모드: {'자동' if auto_execute else '수동'}")
        print("="*80)
        
        # 초기 질문 추가
        self.messages.append(HumanMessage(content=question))
        
        for i in range(max_iterations):
            print(f"\n{'─'*80}")
            print(f"🔄 ITERATION {i+1}/{max_iterations}")
            print(f"{'─'*80}")
            
            # Agent에게 다음 행동 요청
            print("\n💭 Agent가 생각 중...")
            response = self.chat_model.invoke(self.messages)
            
            # 응답 출력 (verbose=True 효과)
            print(f"\n🤖 Agent 응답:")
            print("─" * 60)
            print(response.content)
            print("─" * 60)
            
            self.messages.append(response)
            
            # Final Answer 확인
            if "Final Answer:" in response.content:
                final_answer = self._extract_final_answer(response.content)
                print("\n" + "="*80)
                print("✅ 분석 완료!")
                print("="*80)
                print(f"\n📊 최종 답변:\n{final_answer}")
                print(f"\n📈 총 실행 횟수: {self.execution_count}회")
                return final_answer
            
            # Action Input 추출
            code = self._extract_code(response.content)
            if code:
                # 코드 실행 (자동 또는 수동)
                result = self._execute_code(code, auto_execute)
                
                if result is None:  # 사용자가 건너뛰기 선택
                    observation = "실행이 건너뛰어졌습니다. 다른 방법을 시도하세요."
                else:
                    observation = str(result)
                
                # Observation 추가
                print(f"\n📊 Observation: {observation}")
                self.messages.append(
                    HumanMessage(content=f"Observation: {observation}")
                )
            else:
                print("\n⚠️  Action Input을 찾을 수 없습니다.")
                # Agent에게 다시 요청
                self.messages.append(
                    HumanMessage(content="Action Input을 명확히 제시해주세요.")
                )
        
        print("\n⚠️  최대 반복 횟수 도달")
        return "최대 반복 횟수 초과"
    
    def _extract_code(self, response_text: str) -> Optional[str]:
        """Agent 응답에서 Action Input 코드 추출"""
        
        # 패턴 1: Action Input: 이후 코드
        if "Action Input:" in response_text:
            # Action Input 이후부터 추출
            after_action = response_text.split("Action Input:")[1]
            lines = after_action.split("\n")
            
            code_lines = []
            in_code = False
            
            for line in lines:
                # 빈 줄 이후 첫 줄부터 코드 시작
                if not in_code and line.strip():
                    in_code = True
                
                if in_code:
                    # 종료 조건
                    if line.strip() == "" or \
                       line.startswith("Observation") or \
                       line.startswith("Thought") or \
                       line.startswith("Final Answer"):
                        break
                    code_lines.append(line)
            
            if code_lines:
                return "\n".join(code_lines).strip()
        
        # 패턴 2: ```python 블록
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, response_text, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        return None
    
    def _execute_code(self, code: str, auto_execute: bool):
        """코드 실행 (자동 또는 수동)"""
        
        print(f"\n{'='*60}")
        print("🔧 실행 준비")
        print(f"{'='*60}")
        print("코드:")
        print("─" * 60)
        print(code)
        print("─" * 60)
        
        if not auto_execute:
            # 수동 모드: 사용자 확인
            choice = input("\n▶️  실행하시겠습니까? (y: 실행, n: 건너뛰기, e: 종료): ").lower()
            
            if choice == 'e':
                print("🛑 Agent 종료")
                exit()
            elif choice != 'y':
                print("⏭️  실행 건너뜀")
                return None
        
        # 코드 실행
        try:
            print("\n⏳ 실행 중...")
            
            # 안전한 실행 환경
            safe_globals = {
                "pd": pd,
                "np": np,
                "df": self.df,
                "__builtins__": {
                    "len": len, "sum": sum, "max": max, "min": min,
                    "round": round, "print": print, "str": str,
                    "int": int, "float": float, "list": list, "dict": dict,
                }
            }
            
            local_vars = {}
            exec(code, safe_globals, local_vars)
            
            # 결과 추출
            if "result" in local_vars:
                result = local_vars["result"]
            elif local_vars:
                result = local_vars[list(local_vars.keys())[-1]]
            else:
                result = "실행 완료 (출력 없음)"
            
            self.execution_count += 1
            print(f"✅ 실행 성공! (총 {self.execution_count}회)")
            
            # DataFrame/Series는 요약
            if isinstance(result, pd.DataFrame):
                return f"DataFrame({result.shape[0]}행 x {result.shape[1]}컬럼)\n상위 3개 행:\n{result.head(3).to_string()}"
            elif isinstance(result, pd.Series):
                return f"Series(길이 {len(result)})\n상위 5개:\n{result.head(5).to_string()}"
            else:
                return result
                
        except Exception as e:
            print(f"❌ 에러 발생!")
            return f"에러: {str(e)}"
    
    def _extract_final_answer(self, response_text: str) -> str:
        """Final Answer 추출"""
        if "Final Answer:" in response_text:
            return response_text.split("Final Answer:")[1].strip()
        return response_text
    
    def show_conversation(self):
        """대화 이력 출력"""
        print("\n" + "="*80)
        print("💬 대화 이력")
        print("="*80)
        for i, msg in enumerate(self.messages[1:], 1):  # SystemMessage 제외
            role = "👤 User" if isinstance(msg, HumanMessage) else "🤖 Agent"
            content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"\n[{i}] {role}:")
            print(f"    {content_preview}")

# %% [markdown]
# ---
# # Part 4: Agent 실행 및 체험 (15분)

# %% 4-1. Agent 초기화

print("\n" + "="*80)
print("🚀 Part 4: Pandas Pseudo-Agent 실행")
print("="*80)

# LLM 초기화
chat_model = PotensChatModel()

# Agent 생성
agent = PandasPseudoAgent(chat_model, df)

print("✅ Agent 초기화 완료")

# %% 4-2. 실습 1: 간단한 질문 (자동 모드)

print("\n" + "="*80)
print("📝 실습 1: 간단한 질문 - 자동 실행 모드")
print("="*80)

# 자동 모드로 실행 (빠른 테스트)
agent1 = PandasPseudoAgent(chat_model, df)
result1 = agent1.run(
    question="고객들의 평균 나이는 몇 살인가요?",
    max_iterations=3,
    auto_execute=True  # 자동 실행
)

# %% 4-3. 실습 2: 복잡한 질문 (수동 모드) - 대화형

print("\n" + "="*80)
print("📝 실습 2: 복잡한 질문 - 수동 실행 모드")
print("="*80)
print("💡 각 단계마다 코드를 확인하고 실행 여부를 결정할 수 있습니다.")

# 수동 모드로 실행
agent2 = PandasPseudoAgent(chat_model, df)

# 주석 해제하여 대화형으로 실행
# result2 = agent2.run(
#     question="구매 횟수가 가장 많은 상위 5개 도시를 찾아주세요",
#     max_iterations=5,
#     auto_execute=False  # 수동 실행 - 사용자 확인 필요
# )

print("\n💡 위 주석을 해제하고 실행하면 대화형 Agent를 체험할 수 있습니다!")

# %% 4-4. 실습 3: 멀티스텝 분석 (자동 모드)

print("\n" + "="*80)
print("📝 실습 3: 멀티스텝 분석")
print("="*80)

agent3 = PandasPseudoAgent(chat_model, df)
result3 = agent3.run(
    question="Platinum 등급 고객의 평균 구매액과 전체 평균 구매액을 비교해주세요",
    max_iterations=5,
    auto_execute=True
)

# 대화 이력 확인
agent3.show_conversation()

# %% [markdown]
# ---
# # Part 5: 다양한 질문으로 실험 (보너스)

# %% 5-1. 실험용 질문 모음

SAMPLE_QUESTIONS = [
    "고객 데이터에서 결측치가 있나요?",
    "성별에 따른 평균 구매액 차이를 분석해주세요",
    "구매 횟수와 총 구매액의 상관관계를 계산해주세요",
    "서울 지역 고객 중 Gold 등급 이상인 사람은 몇 명인가요?",
    "나이대별(20대, 30대, 40대, 50대, 60대)로 그룹화해서 평균 구매액을 보여주세요"
]

print("\n" + "="*80)
print("💡 실험해볼 수 있는 질문들:")
print("="*80)
for i, q in enumerate(SAMPLE_QUESTIONS, 1):
    print(f"{i}. {q}")

print("\n사용 예시:")
print("""
agent = PandasPseudoAgent(chat_model, df)
result = agent.run(
    question=SAMPLE_QUESTIONS[0],  # 원하는 질문 선택
    max_iterations=5,
    auto_execute=True
)
""")

# %% [markdown]
# ---
# # 🎉 실습 완료!
# 
# ## 배운 내용:
# 
# ### 1. ReAct 패턴의 핵심
# - ✅ **Thought**: Agent의 "생각" 과정 투명화
# - ✅ **Action/Action Input**: 명확한 실행 계획
# - ✅ **Observation**: 실행 결과 기반 다음 행동 결정
# - ✅ **Final Answer**: 사용자 친화적 답변
# 
# ### 2. Pseudo-Agent의 장점
# - ✅ Function Calling 불필요
# - ✅ 모든 단계를 사람이 확인 가능 (verbose=True 효과)
# - ✅ 안전성: 위험한 코드 실행 방지
# - ✅ 교육적: Agent의 의사결정 과정 학습
# 
# ### 3. 사람-AI 협업 패턴
# - ✅ Agent는 "계획" 수립
# - ✅ 사람은 "검증" 및 "승인"
# - ✅ Agent는 "결과 해석" 및 "다음 단계"
# 
# ## 💡 현실 적용 시 고려사항:
# 
# ### 장점
# - 대부분의 LLM에서 작동 (범용성)
# - 보안 정책 준수 용이
# - 디버깅 및 개선 쉬움
# 
# ### 한계
# - 완전 자동화는 어려움
# - 복잡한 분석은 반복 횟수 증가
# - 코드 파싱 오류 가능성
# 
# ### 극복 방법
# - 프롬프트 튜닝으로 정확도 향상
# - 에러 처리 로직 강화
# - 자주 사용하는 패턴 템플릿화
# 
# ## 🚀 다음 단계:
# - 핸즈온 랩 3에서는 이 Agent를 Streamlit UI로 감싸봅니다!
# - 버튼 클릭으로 코드 실행
# - 대화 이력 시각화
# - CSV 파일 업로드
# 
# ## 💭 생각해볼 질문:
# 1. 완전 자동 Agent vs Pseudo-Agent, 어느 것이 더 실무에 적합할까?
# 2. DA의 역할이 어떻게 변화하는가?
# 3. 어떤 분석 작업을 Agent에게 맡길 수 있을까?