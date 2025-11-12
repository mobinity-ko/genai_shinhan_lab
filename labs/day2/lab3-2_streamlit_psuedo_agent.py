"""
핸즈온 랩 3: Streamlit + Pseudo-Agent 연동
파일명: app.py
실행: streamlit run app.py

소요 시간: 45분
난이도: ⭐⭐⭐

학습 목표:
1. Streamlit으로 대화형 UI 구축
2. session_state로 대화 이력 관리
3. CSV 파일 업로드 및 분석
4. Pseudo-Agent와 실시간 협업
"""

import streamlit as st
import pandas as pd
import re
from io import StringIO

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from potens_wrapper import PotensChatModel  # 랩 1,2에서 만든 Wrapper 사용

# ============================================================================
# Part 1: 페이지 설정 및 초기화
# ============================================================================

st.set_page_config(
    page_title="AI 데이터 분석 어시스턴트",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI 데이터 분석 어시스턴트")
st.caption("POTENS LLM 기반 대화형 데이터 분석 도구")

# ============================================================================
# Part 2: LLM 초기화 (캐싱으로 재사용)
# ============================================================================

@st.cache_resource
def get_chat_model():
    """LLM을 한 번만 초기화하고 재사용"""
    return PotensChatModel()

chat_model = get_chat_model()

# ============================================================================
# Part 3: 세션 상태 초기화
# ============================================================================

# ReAct 시스템 프롬프트
REACT_SYSTEM_PROMPT = """
당신은 데이터 분석 전문가입니다.

사용자의 요청을 수행하기 위해 다음 형식으로 답변하세요:

Thought: (무엇을 해야 할지 생각)
Action: python_repl
Action Input: (실행할 Python 코드)

사용자가 "Observation: [결과]"를 제공하면, 그 결과를 분석하고 다음 행동을 결정하세요.

최종 답변이 준비되면:
Final Answer: [최종 답변]

**중요:**
- 한 번에 하나의 Action만 제안
- 코드는 실행 가능한 완전한 형태로 작성
- 데이터프레임 변수명은 'df'를 사용
"""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content=REACT_SYSTEM_PROMPT)
    ]

if "df" not in st.session_state:
    st.session_state.df = None

if "pending_code" not in st.session_state:
    st.session_state.pending_code = None

# ============================================================================
# Part 4: 사이드바 - 데이터 업로드 및 설정
# ============================================================================

with st.sidebar:
    st.header("⚙️ 설정")
    
    # CSV 파일 업로드
    uploaded_file = st.file_uploader(
        "CSV 파일 업로드",
        type=["csv"],
        help="분석할 CSV 파일을 업로드하세요"
    )
    
    if uploaded_file is not None:
        # CSV 읽기
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success(f"✅ 파일 로드 완료: {uploaded_file.name}")
        
        # 데이터 미리보기
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(st.session_state.df.head(10))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("행 수", len(st.session_state.df))
            with col2:
                st.metric("컬럼 수", len(st.session_state.df.columns))
            
            st.write("**컬럼 정보:**")
            st.write(st.session_state.df.dtypes)
    
    st.divider()
    
    # 대화 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = [
            SystemMessage(content=REACT_SYSTEM_PROMPT)
        ]
        st.session_state.pending_code = None
        st.rerun()
    
    st.divider()
    
    # 사용 가이드
    with st.expander("📖 사용 가이드"):
        st.markdown("""
        **1단계: 데이터 업로드**
        - CSV 파일을 업로드하세요
        
        **2단계: 질문하기**
        - "평균 나이를 구해줘"
        - "상관관계 분석해줘"
        - "인사이트 3개 찾아줘"
        
        **3단계: 코드 실행**
        - Agent가 제안한 코드 확인
        - "실행" 버튼 클릭
        - 결과가 자동으로 Agent에게 전달됨
        
        **팁:**
        - 구체적으로 질문할수록 좋은 결과
        - 단계별로 진행 상황 확인 가능
        """)

# ============================================================================
# Part 5: 메인 영역 - 대화 인터페이스
# ============================================================================

# 이전 대화 표시 (SystemMessage 제외)
for msg in st.session_state.messages[1:]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# ============================================================================
# Part 6: 코드 추출 및 실행 함수
# ============================================================================

def extract_code(response_text):
    """
    Agent 응답에서 Action Input 코드 추출
    
    패턴:
    1. Action Input: 다음 줄부터 빈 줄까지
    2. ```python ... ``` 블록
    """
    # 패턴 1: Action Input: 이후
    if "Action Input:" in response_text:
        lines = response_text.split("Action Input:")[1].split("\n")
        code_lines = []
        for line in lines[1:]:  # Action Input: 다음 줄부터
            if line.strip() == "" or line.startswith("Observation") or line.startswith("Thought"):
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

def safe_exec(code, context):
    """
    코드를 안전하게 실행
    
    Args:
        code: 실행할 Python 코드
        context: 실행 컨텍스트 (예: {"df": dataframe})
    
    Returns:
        실행 결과 또는 에러 메시지
    """
    try:
        # 허용된 globals (보안을 위해 제한)
        safe_globals = {
            "pd": pd,
            "df": context.get("df"),
            "__builtins__": {
                "len": len,
                "sum": sum,
                "max": max,
                "min": min,
                "round": round,
                "print": print,
            }
        }
        
        # 로컬 변수 저장용
        local_vars = {}
        
        # 코드 실행
        exec(code, safe_globals, local_vars)
        
        # 결과 추출 (마지막 변수 또는 출력)
        if local_vars:
            # 'result' 변수가 있으면 반환
            if "result" in local_vars:
                return local_vars["result"]
            # 아니면 마지막 변수 반환
            return local_vars[list(local_vars.keys())[-1]]
        
        return "✅ 실행 완료 (출력 없음)"
        
    except Exception as e:
        return f"❌ 에러: {str(e)}"

# ============================================================================
# Part 7: Pending Code 실행 UI
# ============================================================================

if st.session_state.pending_code:
    st.info("💡 Agent가 코드를 제안했습니다. 확인 후 실행하세요.")
    
    with st.expander("🔧 제안된 코드", expanded=True):
        st.code(st.session_state.pending_code, language="python")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ 실행", type="primary", use_container_width=True):
                if st.session_state.df is None:
                    st.error("⚠️ 먼저 CSV 파일을 업로드하세요!")
                else:
                    with st.spinner("실행 중..."):
                        # 코드 실행
                        result = safe_exec(
                            st.session_state.pending_code,
                            {"df": st.session_state.df}
                        )
                        
                        # 결과 표시
                        st.success("✅ 실행 완료")
                        st.write("**결과:**")
                        st.write(result)
                        
                        # Observation을 메시지에 추가
                        observation_msg = f"Observation: {result}"
                        st.session_state.messages.append(
                            HumanMessage(content=observation_msg)
                        )
                        
                        # Agent에게 다음 행동 요청
                        with st.spinner("Agent 응답 대기..."):
                            response = chat_model.invoke(st.session_state.messages)
                            st.session_state.messages.append(response)
                        
                        # Pending code 초기화
                        st.session_state.pending_code = None
                        st.rerun()
        
        with col2:
            if st.button("⏭️ 건너뛰기", use_container_width=True):
                # 건너뛰기 메시지 추가
                st.session_state.messages.append(
                    HumanMessage(content="Observation: (실행 건너뜀. 다른 방법을 시도하세요)")
                )
                
                # Agent에게 다시 요청
                with st.spinner("Agent 응답 대기..."):
                    response = chat_model.invoke(st.session_state.messages)
                    st.session_state.messages.append(response)
                
                st.session_state.pending_code = None
                st.rerun()

# ============================================================================
# Part 8: 사용자 입력 처리
# ============================================================================

if user_input := st.chat_input("분석 요청을 입력하세요... (예: '평균 나이를 구해줘')"):
    # 데이터 업로드 확인
    if st.session_state.df is None:
        st.error("⚠️ 먼저 CSV 파일을 업로드하세요!")
        st.stop()
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(user_input)
    
    # 메시지 이력에 추가
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    # Agent 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = chat_model.invoke(st.session_state.messages)
            st.write(response.content)
    
    # 응답을 이력에 추가
    st.session_state.messages.append(response)
    
    # Action Input이 있으면 pending_code로 저장
    code = extract_code(response.content)
    if code and "Final Answer:" not in response.content:
        st.session_state.pending_code = code
    
    # 페이지 새로고침
    st.rerun()

# ============================================================================
# Part 9: 푸터
# ============================================================================

st.divider()
st.caption("💡 Tip: Agent의 제안을 신뢰하되, 항상 코드를 확인하세요!")

# ============================================================================
# 실행 방법
# ============================================================================
"""
터미널에서 실행:
    streamlit run app.py

필요한 파일:
    - potens_wrapper.py (랩 1,2에서 작성)
    - .env (POTENS_API_KEY 포함)
    - sample.csv (테스트용 데이터)

주요 기능:
    ✅ CSV 파일 업로드
    ✅ 대화형 분석 요청
    ✅ Agent의 코드 제안 확인
    ✅ 안전한 코드 실행
    ✅ 자동 Observation 전달
    ✅ 멀티턴 대화 이력 관리
"""