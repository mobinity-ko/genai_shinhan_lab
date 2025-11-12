"""
핸즈온 랩 4: 자율적 EDA (탐색적 데이터 분석) Agent
소요 시간: 30분
난이도: ⭐⭐⭐⭐

학습 목표:
1. 포괄적 목표를 자율적으로 달성하는 Agent 구축
2. EDA 프로세스의 자동화
3. 비즈니스 인사이트 자동 발굴
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from potens_wrapper import PotensChatModel

# %% [markdown]
# # Part 1: EDA Agent 시스템 프롬프트 (10분)
# 
# ## 🎯 일반 Agent vs EDA Agent
# 
# | 일반 Agent | EDA Agent |
# |-----------|-----------|
# | "평균을 구해줘" (구체적) | "인사이트를 찾아줘" (포괄적) |
# | 1~2단계 실행 | 5~10단계 자율 실행 |
# | 명확한 종료 조건 | 목표 달성까지 반복 |

# %% 1-1. EDA Agent 전용 시스템 프롬프트

EDA_SYSTEM_PROMPT = """
당신은 탐색적 데이터 분석(EDA) 전문가입니다.

**목표:** 사용자가 제공한 목표를 달성하기 위해 자율적으로 데이터를 분석하세요.

**분석 프로세스:**
1. 데이터 기본 구조 파악 (shape, dtypes, describe)
2. 결측치 및 이상치 확인
3. 주요 변수 간 관계 분석 (correlation, groupby)
4. 패턴 및 이상 현상 탐지
5. 비즈니스 인사이트 도출

**형식:**
Thought: (현재 단계에서 무엇을 해야 할지)
Action: python_repl
Action Input: (실행할 Python 코드)

사용자가 "Observation: [결과]"를 제공하면 분석을 계속하세요.

**최종 답변 형식:**
Final Answer: 
## 인사이트 1: [제목]
- 발견: [구체적 수치와 함께]
- 의미: [비즈니스적 해석]
- 제안: [액션 아이템]

## 인사이트 2: ...

## 인사이트 3: ...

**중요 규칙:**
- 각 분석은 이전 결과를 기반으로 진행
- 인사이트는 구체적 수치 포함
- 비즈니스 가치를 명확히 설명
- 최소 3개 이상의 인사이트 도출
"""

print("✅ EDA Agent 시스템 프롬프트 정의 완료")

# %% [markdown]
# ---
# # Part 2: EDA Agent 클래스 구현 (10분)

# %% 2-1. EDA Agent 클래스

class EDAAgent:
    """
    자율적으로 EDA를 수행하는 Agent
    """
    
    def __init__(self, chat_model: PotensChatModel, df: pd.DataFrame):
        self.chat_model = chat_model
        self.df = df
        self.messages = [SystemMessage(content=EDA_SYSTEM_PROMPT)]
        self.execution_history = []
    
    def run(self, goal: str, max_iterations: int = 10):
        """
        목표를 달성할 때까지 자율적으로 분석
        
        Args:
            goal: 분석 목표 (예: "매출 증대를 위한 인사이트 3개 찾기")
            max_iterations: 최대 반복 횟수
        
        Returns:
            최종 인사이트
        """
        print("="*80)
        print("🤖 EDA Agent 시작")
        print("="*80)
        print(f"📊 데이터: {self.df.shape[0]}행 x {self.df.shape[1]}컬럼")
        print(f"🎯 목표: {goal}")
        print(f"🔄 최대 반복: {max_iterations}회")
        print("="*80)
        
        # 초기 메시지: 목표 + 데이터 정보
        data_info = self._get_data_info()
        initial_message = f"""
**목표:** {goal}

**데이터 정보:**
{data_info}

위 목표를 달성하기 위해 단계별로 분석을 시작하세요.
"""
        self.messages.append(HumanMessage(content=initial_message))
        
        # 반복 실행
        for i in range(max_iterations):
            print(f"\n{'─'*80}")
            print(f"🔄 반복 {i+1}/{max_iterations}")
            print(f"{'─'*80}")
            
            # Agent에게 다음 행동 요청
            response = self.chat_model.invoke(self.messages)
            print(f"\n🤖 Agent 응답:\n{response.content[:500]}...")
            
            self.messages.append(response)
            
            # Final Answer 확인
            if "Final Answer:" in response.content:
                print("\n" + "="*80)
                print("✅ EDA 완료!")
                print("="*80)
                return self._extract_final_answer(response.content)
            
            # Action Input 추출 및 실행
            code = self._extract_code(response.content)
            if code:
                print(f"\n📝 실행할 코드:\n{code}")
                
                # 코드 실행
                result = self._safe_exec(code)
                print(f"\n📊 실행 결과:\n{result}")
                
                # 실행 이력 저장
                self.execution_history.append({
                    "iteration": i + 1,
                    "code": code,
                    "result": result
                })
                
                # Observation 추가
                self.messages.append(
                    HumanMessage(content=f"Observation: {result}")
                )
            else:
                print("\n⚠️ Action Input을 찾을 수 없습니다. 프롬프트를 조정하세요.")
                break
        
        print("\n⚠️ 최대 반복 횟수 도달")
        return "최대 반복 횟수 초과. Final Answer를 받지 못했습니다."
    
    def _get_data_info(self) -> str:
        """데이터 기본 정보 생성"""
        info_lines = [
            f"- Shape: {self.df.shape[0]}행 x {self.df.shape[1]}컬럼",
            f"- 컬럼: {', '.join(self.df.columns.tolist())}",
            f"- 타입: {self.df.dtypes.to_dict()}",
            f"- 결측치: {self.df.isnull().sum().to_dict()}",
        ]
        return "\n".join(info_lines)
    
    def _extract_code(self, response_text: str) -> str:
        """Agent 응답에서 코드 추출"""
        # Action Input: 다음 줄부터
        if "Action Input:" in response_text:
            lines = response_text.split("Action Input:")[1].split("\n")
            code_lines = []
            for line in lines[1:]:
                if line.strip() == "" or "Observation" in line or "Thought" in line:
                    break
                code_lines.append(line)
            if code_lines:
                return "\n".join(code_lines).strip()
        
        # ```python 블록
        pattern = r"```python\s*(.*?)\s*```"
        matches = re.findall(pattern, response_text, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        return None
    
    def _safe_exec(self, code: str) -> Any:
        """코드를 안전하게 실행"""
        try:
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
                result = "✅ 실행 완료"
            
            # DataFrame은 요약 정보만
            if isinstance(result, pd.DataFrame):
                return f"DataFrame({result.shape[0]}행 x {result.shape[1]}컬럼)\n{result.head(3).to_string()}"
            elif isinstance(result, pd.Series):
                return f"Series(길이 {len(result)})\n{result.head(5).to_string()}"
            else:
                return str(result)
                
        except Exception as e:
            return f"❌ 에러: {str(e)}"
    
    def _extract_final_answer(self, response_text: str) -> str:
        """Final Answer 추출"""
        if "Final Answer:" in response_text:
            return response_text.split("Final Answer:")[1].strip()
        return response_text
    
    def show_history(self):
        """실행 이력 표시"""
        print("\n" + "="*80)
        print("📜 실행 이력")
        print("="*80)
        for item in self.execution_history:
            print(f"\n[{item['iteration']}회차]")
            print(f"코드: {item['code'][:100]}...")
            print(f"결과: {str(item['result'])[:100]}...")

# %% [markdown]
# ---
# # Part 3: 샘플 데이터 생성 및 테스트 (10분)

# %% 3-1. 샘플 데이터 생성

# 전자상거래 매출 데이터 생성
np.random.seed(42)

n_customers = 1000

sample_df = pd.DataFrame({
    'customer_id': range(1, n_customers + 1),
    'age': np.random.randint(20, 70, n_customers),
    'gender': np.random.choice(['M', 'F'], n_customers),
    'region': np.random.choice(['서울', '경기', '부산', '기타'], n_customers),
    'purchase_count': np.random.poisson(5, n_customers),
    'total_amount': np.random.exponential(300000, n_customers),
    'avg_rating': np.random.uniform(1, 5, n_customers),
    'is_premium': np.random.choice([0, 1], n_customers, p=[0.7, 0.3])
})

# 일부러 패턴 추가 (인사이트 발굴용)
# 프리미엄 고객은 구매액이 높음
sample_df.loc[sample_df['is_premium'] == 1, 'total_amount'] *= 2

# 서울 고객의 평균 평점이 높음
sample_df.loc[sample_df['region'] == '서울', 'avg_rating'] += 0.5
sample_df['avg_rating'] = sample_df['avg_rating'].clip(1, 5)

# 연령대별 구매 패턴 (40대가 가장 많이 구매)
sample_df.loc[sample_df['age'].between(40, 49), 'purchase_count'] += 2

print("✅ 샘플 데이터 생성 완료")
print(sample_df.head())

# %% 3-2. EDA Agent 실행

# Agent 초기화
chat_model = PotensChatModel()
eda_agent = EDAAgent(chat_model, sample_df)

# 실행
insights = eda_agent.run(
    goal="매출 증대를 위한 실행 가능한 비즈니스 인사이트 3개를 찾아주세요",
    max_iterations=8
)

# 최종 결과 출력
print("\n" + "="*80)
print("📊 최종 인사이트")
print("="*80)
print(insights)

# %% 3-3. 실행 이력 확인

eda_agent.show_history()

# %% [markdown]
# ---
# # Part 4: 심화 - 특정 도메인 EDA Agent (보너스)

# %% 4-1. 도메인별 프롬프트 템플릿

def create_domain_eda_prompt(domain: str) -> str:
    """도메인별 맞춤형 EDA 프롬프트 생성"""
    
    domain_templates = {
        "금융": """
당신은 금융 데이터 분석 전문가입니다.

**주요 분석 포인트:**
- 리스크 지표 (연체율, 부도율)
- 수익성 지표 (ROI, 마진)
- 고객 세그먼트별 특성
- 시계열 트렌드 (계절성, 추세)

**특별 주의사항:**
- 이상 거래 패턴 탐지
- 규제 준수 고려
- 민감 정보 보호
""",
        "마케팅": """
당신은 마케팅 데이터 분석 전문가입니다.

**주요 분석 포인트:**
- 고객 세그먼테이션
- 전환율 및 이탈률
- 채널별 효율성
- LTV (고객 생애 가치)

**특별 주의사항:**
- 캠페인 ROI 측정
- 타겟 고객군 특정
- A/B 테스트 결과 해석
""",
        "운영": """
당신은 운영 데이터 분석 전문가입니다.

**주요 분석 포인트:**
- 효율성 지표 (처리 시간, 비용)
- 병목 구간 탐지
- 자원 활용률
- 품질 지표

**특별 주의사항:**
- 프로세스 개선 기회 발굴
- 이상치 원인 분석
- 예측 유지보수
"""
    }
    
    base_prompt = EDA_SYSTEM_PROMPT
    domain_specific = domain_templates.get(domain, "")
    
    return base_prompt + "\n" + domain_specific

# 예시
financial_prompt = create_domain_eda_prompt("금융")
print("✅ 도메인별 프롬프트 생성 완료")

# %% [markdown]
# ---
# # 🎉 실습 완료!
# 
# ## 배운 내용:
# 1. ✅ 자율적 EDA Agent 구현
#    - 포괄적 목표 설정
#    - 다단계 자동 분석
#    - 비즈니스 인사이트 도출
# 
# 2. ✅ Agent의 실행 흐름 관찰
#    - 각 단계별 의사결정
#    - 이전 결과 기반 다음 행동
#    - 목표 달성까지 반복
# 
# 3. ✅ 실무 적용 포인트
#    - 반복 작업 자동화
#    - 탐색 시간 단축
#    - DA는 검증 및 심화에 집중
# 
# ## 💡 한계와 개선 방향:
# 
# **현재 한계:**
# - 최대 반복 횟수 제한
# - 복잡한 통계 분석 어려움
# - 시각화 자동 생성 불가
# - 코드 파싱 오류 가능성
# 
# **개선 방향:**
# 1. Function Calling 지원 시 완전 자동화
# 2. 플롯 생성 도구 추가
# 3. 도메인별 프롬프트 고도화
# 4. 실행 결과 캐싱으로 속도 개선
# 
# ## 🚀 다음 단계:
# - 실제 업무 데이터로 테스트
# - 도메인 지식을 프롬프트에 반영
# - Streamlit과 통합하여 UI 구축
# - 팀원들과 인사이트 공유 프로세스 구축
# 
# ## 💭 토의 주제:
# 1. 완전 자동화 vs 반자동화의 장단점은?
# 2. DA의 역할이 어떻게 변화하는가?
# 3. 실무 적용 시 예상되는 장애물은?