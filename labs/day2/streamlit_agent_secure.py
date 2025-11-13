"""
보안 강화: 데이터를 외부로 보내지 않는 Agent 패턴

핵심 원칙:
1. 데이터 스키마만 전달 (실제 값 X)
2. Observation은 "메타정보"만 전달
3. 민감한 결과는 로컬에만 표시
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from potens_wrapper import PotensChatModel

# ============================================================================
# Part 1: 안전한 시스템 프롬프트 (스키마만 전달)
# ============================================================================

def create_safe_system_prompt(df: pd.DataFrame) -> str:
    """
    데이터의 스키마 정보만 추출 (실제 값은 포함 X)
    """
    schema_info = {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "columns": {
            col: {
                "dtype": str(df[col].dtype),
                "has_null": df[col].isnull().any(),
                # ❌ 실제 값은 포함하지 않음!
            }
            for col in df.columns
        }
    }
    
    prompt = f"""
당신은 Pandas 데이터 분석 전문가입니다.

**데이터 스키마 (메타정보만):**
- 행 수: {schema_info['num_rows']}
- 컬럼 수: {schema_info['num_columns']}
- 컬럼 정보:
"""
    
    for col, info in schema_info['columns'].items():
        prompt += f"\n  - {col}: {info['dtype']}, 결측치={'있음' if info['has_null'] else '없음'}"
    
    prompt += """

**중요: 데이터는 사용자의 로컬 환경에만 존재합니다.**
당신은 코드만 생성하고, 사용자가 로컬에서 실행합니다.

형식:
Thought: (분석 계획)
Action: python_repl
Action Input: (Pandas 코드, result 변수에 저장)

Observation을 받으면 해석하고 다음 단계를 제안하세요.
"""
    
    return prompt

# ============================================================================
# Part 2: 안전한 Observation 생성 (요약만 전달)
# ============================================================================

def create_safe_observation(result: Any, max_items: int = 3) -> str:
    """
    실행 결과를 안전하게 요약
    
    원칙:
    - 통계값: OK (평균, 개수 등)
    - 실제 데이터: NG (이름, ID, 금액 등)
    """
    
    # None 처리
    if result is None:
        return "실행 완료 (출력 없음)"
    
    # DataFrame
    if isinstance(result, pd.DataFrame):
        # ⚠️ 실제 데이터는 보내지 않음!
        return f"""
DataFrame 결과:
- Shape: {result.shape[0]}행 x {result.shape[1]}컬럼
- 컬럼: {', '.join(result.columns)}
- 데이터 타입: {result.dtypes.to_dict()}
(실제 데이터는 로컬에만 표시됩니다)
"""
    
    # Series
    elif isinstance(result, pd.Series):
        return f"""
Series 결과:
- 길이: {len(result)}
- 데이터 타입: {result.dtype}
(실제 데이터는 로컬에만 표시됩니다)
"""
    
    # 숫자 (통계값)
    elif isinstance(result, (int, float)):
        return f"결과: {result}"
    
    # 문자열 (짧으면 OK)
    elif isinstance(result, str):
        if len(result) < 100:
            return f"결과: {result}"
        else:
            return f"결과: (긴 텍스트, {len(result)}자)"
    
    # 리스트/딕셔너리 (개수만)
    elif isinstance(result, (list, dict)):
        return f"결과: {type(result).__name__} (길이 {len(result)})"
    
    # 기타
    else:
        return f"결과 타입: {type(result).__name__}"

# ============================================================================
# Part 3: 보안 강화 Agent 클래스
# ============================================================================

class SecurePandasAgent:
    """
    데이터를 외부로 보내지 않는 안전한 Agent
    """
    
    def __init__(self, chat_model: PotensChatModel, df: pd.DataFrame):
        self.chat_model = chat_model
        self.df = df
        self.messages = []
        
        # 스키마만 포함된 시스템 프롬프트
        safe_prompt = create_safe_system_prompt(df)
        self.messages.append(SystemMessage(content=safe_prompt))
        
        print("✅ 보안 설정 완료:")
        print("   - 데이터 스키마만 LLM에 전달")
        print("   - 실제 값은 로컬에만 유지")
    
    def run(self, question: str, max_iterations: int = 5):
        """안전하게 분석 실행"""
        
        print(f"\n{'='*80}")
        print(f"🔒 보안 Agent 실행")
        print(f"{'='*80}")
        print(f"질문: {question}")
        
        self.messages.append(HumanMessage(content=question))
        
        for i in range(max_iterations):
            print(f"\n{'─'*60}")
            print(f"반복 {i+1}/{max_iterations}")
            
            # LLM 호출
            response = self.chat_model.invoke(self.messages)
            print(f"\n🤖 Agent:\n{response.content[:300]}...")
            
            self.messages.append(response)
            
            # Final Answer 확인
            if "Final Answer:" in response.content:
                return self._extract_final_answer(response.content)
            
            # 코드 추출
            code = self._extract_code(response.content)
            if code:
                print(f"\n💻 생성된 코드:\n{code}")
                
                # 로컬 실행
                result = self._execute_locally(code)
                
                print(f"\n📊 실제 결과 (로컬에만 표시):")
                print(result)
                
                # 안전한 Observation 생성
                safe_obs = create_safe_observation(result)
                print(f"\n📤 LLM에 전달되는 정보:\n{safe_obs}")
                
                self.messages.append(
                    HumanMessage(content=f"Observation: {safe_obs}")
                )
        
        return "최대 반복 초과"
    
    def _execute_locally(self, code: str) -> Any:
        """로컬에서만 코드 실행 (결과를 외부로 보내지 않음)"""
        try:
            safe_globals = {
                "pd": pd,
                "np": np,
                "df": self.df,
                "__builtins__": {}
            }
            
            local_vars = {}
            exec(code, safe_globals, local_vars)
            
            return local_vars.get("result", "실행 완료")
        except Exception as e:
            return f"에러: {str(e)}"
    
    def _extract_code(self, text: str) -> Optional[str]:
        """코드 추출"""
        if "Action Input:" in text:
            lines = text.split("Action Input:")[1].split("\n")
            code_lines = []
            for line in lines[1:]:
                if line.strip() == "" or "Observation" in line or "Thought" in line:
                    break
                code_lines.append(line)
            return "\n".join(code_lines).strip() if code_lines else None
        return None
    
    def _extract_final_answer(self, text: str) -> str:
        """Final Answer 추출"""
        if "Final Answer:" in text:
            return text.split("Final Answer:")[1].strip()
        return text

# ============================================================================
# Part 4: 보안 vs 비보안 비교 데모
# ============================================================================

def demo_security_comparison():
    """보안 강화 전/후 비교"""
    
    # 샘플 데이터
    df = pd.DataFrame({
        'customer_name': ['김철수', '이영희', '박민수'],  # 민감 정보
        'age': [25, 35, 45],
        'salary': [5000, 6000, 7000]  # 민감 정보
    })
    
    print("="*80)
    print("🔒 보안 비교 데모")
    print("="*80)
    
    # 기존 방식 (비보안)
    print("\n❌ 기존 방식 - LLM에 전달되는 내용:")
    print("─"*60)
    unsafe_prompt = f"""
데이터프레임 정보:
{df.to_string()}

데이터 요약:
{df.describe().to_string()}
"""
    print(unsafe_prompt)
    print("→ 실제 이름, 연봉 등이 모두 노출! ❌")
    
    # 보안 방식
    print("\n✅ 보안 방식 - LLM에 전달되는 내용:")
    print("─"*60)
    safe_prompt = create_safe_system_prompt(df)
    print(safe_prompt)
    print("\n→ 스키마만 전달, 실제 값은 로컬에만! ✅")
    
    print("\n" + "="*80)
    print("📊 Observation 비교")
    print("="*80)
    
    result = df['salary'].mean()
    
    print("\n❌ 기존 방식:")
    print(f"   Observation: {result}")
    print("   → 실제 연봉 평균값 노출")
    
    print("\n✅ 보안 방식:")
    safe_obs = create_safe_observation(result)
    print(f"   {safe_obs}")
    print("   → 통계값은 OK (개인 식별 불가)")

# ============================================================================
# Part 5: Streamlit 적용 예시
# ============================================================================

STREAMLIT_SECURE_TEMPLATE = '''
"""
보안 강화 Streamlit 앱
"""
import streamlit as st
from secure_agent import SecurePandasAgent, create_safe_observation
from potens_wrapper import PotensChatModel

st.title("🔒 보안 강화 데이터 분석 앱")

# 보안 경고 표시
st.info("""
🔒 **데이터 보안 정책:**
- ✅ 데이터는 귀하의 PC에만 저장됩니다
- ✅ LLM에는 스키마(구조) 정보만 전달됩니다
- ✅ 실제 값은 외부로 전송되지 않습니다
- ✅ 분석 결과는 로컬에서만 표시됩니다
""")

# CSV 업로드
uploaded_file = st.file_uploader("CSV 업로드", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # 데이터 보안 정보 표시
    with st.expander("📊 데이터 정보 (로컬에만 표시)"):
        st.dataframe(df.head())
        st.caption("⚠️ 이 데이터는 화면에만 표시되며 LLM으로 전송되지 않습니다")
    
    # LLM 초기화
    llm = PotensChatModel()
    agent = SecurePandasAgent(llm, df)
    
    # 사용자 질문
    if question := st.chat_input("질문을 입력하세요"):
        with st.spinner("분석 중..."):
            # Agent 실행
            result = agent.run(question)
            
            st.success("분석 완료!")
            st.write(result)
        
        # 보안 로그 표시
        with st.expander("🔍 보안 로그 (무엇이 전송되었는지 확인)"):
            st.write("**LLM에 전달된 정보:**")
            for msg in agent.messages:
                if isinstance(msg, HumanMessage):
                    st.text(f"User: {msg.content[:200]}...")
'''

# ============================================================================
# Part 6: 실행 및 테스트
# ============================================================================

if __name__ == "__main__":
    # 데모 실행
    demo_security_comparison()
    
    print("\n" + "="*80)
    print("📚 교육 과정에 반영할 내용")
    print("="*80)
    print("""
1. 오프닝 세션에서 강조:
   "데이터는 PC를 벗어나지 않습니다"
   
2. Agent 구축 시:
   - ✅ 스키마만 전달
   - ✅ Observation은 요약만
   - ✅ 민감 정보 필터링
   
3. 실습 자료 수정:
   - create_safe_system_prompt() 사용
   - create_safe_observation() 적용
   - 보안 체크리스트 제공
   
4. 토의 주제 추가:
   Q: "어떤 정보까지 LLM에 보내도 괜찮을까?"
   A: 스키마, 통계값(평균/개수) OK
      실제 이름, ID, 금액 등 NG
    """)