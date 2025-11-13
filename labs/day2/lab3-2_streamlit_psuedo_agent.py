"""
핸즈온 랩 3: Streamlit + Pseudo-Agent 연동 (최종 완전 버전)
파일명: app.py
실행: streamlit run app.py

🔧 최종 수정 v3:
- 표현식 평가 (eval) 추가 ⭐ 핵심!
- print 출력 캡처
- PyArrow 에러 해결
"""

import streamlit as st
import pandas as pd
import re
import sys
from io import StringIO

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from potens_wrapper import PotensChatModel

# ============================================================================
# Part 1: 페이지 설정
# ============================================================================

st.set_page_config(
    page_title="AI 데이터 분석 어시스턴트",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI 데이터 분석 어시스턴트")
st.caption("POTENS LLM 기반 대화형 데이터 분석 도구")

# ============================================================================
# Part 2: LLM 초기화
# ============================================================================

@st.cache_resource
def get_chat_model():
    return PotensChatModel()

chat_model = get_chat_model()

# ============================================================================
# Part 3: 세션 상태 초기화
# ============================================================================

REACT_SYSTEM_PROMPT = """
당신은 데이터 분석 전문가입니다.

사용자의 요청을 수행하기 위해 다음 형식으로 답변하세요:

Thought: (무엇을 해야 할지 생각)
Action: python_repl
Action Input:
(실행할 Python 코드를 여기에 작성)

사용자가 "Observation: [결과]"를 제공하면, 그 결과를 분석하고 다음 행동을 결정하세요.

최종 답변이 준비되면:
Final Answer: [최종 답변]

**중요 규칙:**
- 한 번에 하나의 Action만 제안
- 데이터프레임 변수명은 'df'를 사용
- Action Input 다음 줄에 코드를 작성하세요
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=REACT_SYSTEM_PROMPT)]

if "df" not in st.session_state:
    st.session_state.df = None

if "pending_code" not in st.session_state:
    st.session_state.pending_code = None

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

# ============================================================================
# Part 4: 사이드바
# ============================================================================

with st.sidebar:
    st.header("⚙️ 설정")
    
    uploaded_file = st.file_uploader(
        "CSV 파일 업로드",
        type=["csv"],
        help="분석할 CSV 파일을 업로드하세요"
    )
    
    if uploaded_file is not None:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success(f"✅ 파일 로드 완료: {uploaded_file.name}")
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(st.session_state.df.head(10))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("행 수", len(st.session_state.df))
            with col2:
                st.metric("컬럼 수", len(st.session_state.df.columns))
    
    st.divider()
    
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=REACT_SYSTEM_PROMPT)]
        st.session_state.pending_code = None
        st.rerun()
    
    st.session_state.debug_mode = st.checkbox("🐛 디버그 모드", value=False)
    
    st.divider()
    
    with st.expander("📖 사용 가이드"):
        st.markdown("""
        **질문 예시:**
        - "평균 나이를 구해줘"
        - "도시별 평균 연봉을 보여줘"
        - "컬럼 목록을 보여줘"
        """)

# ============================================================================
# Part 5: 대화 표시
# ============================================================================

for msg in st.session_state.messages[1:]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# ============================================================================
# Part 6: 코드 추출 및 실행 함수 (최종 완전 버전)
# ============================================================================

def extract_code(response_text):
    """Agent 응답에서 코드 추출 (강화 버전)"""
    
    if st.session_state.debug_mode:
        with st.expander("🔍 디버그: 원본 응답"):
            st.code(response_text)
    
    # 패턴 1: ```python ... ``` 블록 먼저 시도
    pattern = r"```(?:python)?\s*(.*?)\s*```"
    matches = re.findall(pattern, response_text, re.DOTALL)
    if matches:
        code = matches[0].strip()
        # 주석 제거 (선택사항)
        code = "\n".join(line for line in code.split("\n") if not line.strip().startswith("#"))
        if code:
            if st.session_state.debug_mode:
                st.success("✅ 코드 블록에서 추출")
            return code
    
    # 패턴 2: Action Input: 이후
    if "Action Input:" in response_text:
        after_action_input = response_text.split("Action Input:")[1]
        lines = after_action_input.split("\n")
        
        code_lines = []
        in_code_block = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 코드 블록 시작 감지
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            
            # 종료 조건
            if not in_code_block:
                if stripped.startswith("Observation") or \
                   stripped.startswith("Thought") or \
                   stripped.startswith("Final Answer") or \
                   stripped.startswith("Action:"):
                    break
                
                # 빈 줄이고 이미 코드가 있으면 종료
                if not stripped and code_lines:
                    break
            
            # 첫 줄이면서 코드가 있으면 추가
            if i == 0 and stripped and not stripped.startswith("```"):
                code_lines.append(line)
            # 코드 블록 안이거나 일반 코드
            elif stripped or in_code_block:
                code_lines.append(line)
        
        if code_lines:
            code = "\n".join(code_lines).strip()
            if code:
                if st.session_state.debug_mode:
                    st.success("✅ Action Input에서 추출")
                return code
    
    if st.session_state.debug_mode:
        st.warning("⚠️ 코드를 찾을 수 없습니다")
    
    return None

def safe_exec(code, context):
    """
    코드를 안전하게 실행 (최종 완전 버전)
    
    핵심 개선:
    1. 표현식(expression) 평가 ⭐
    2. print 출력 캡처
    3. PyArrow 에러 방지
    """
    try:
        # stdout 캡처
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        # 허용된 globals
        safe_globals = {
            "pd": pd,
            "df": context.get("df"),
            "__builtins__": {
                "len": len, "sum": sum, "max": max, "min": min,
                "round": round, "print": print, "str": str,
                "int": int, "float": float, "list": list, "dict": dict,
                "range": range, "enumerate": enumerate, "sorted": sorted,
                "abs": abs, "any": any, "all": all,
            }
        }
        
        local_vars = {}
        
        if st.session_state.debug_mode:
            with st.expander("🔍 디버그: 실행할 코드"):
                st.code(code, language="python")
        
        # ⭐ 핵심: 표현식인지 문장인지 확인
        # 먼저 exec로 실행 시도
        try:
            exec(code, safe_globals, local_vars)
        except SyntaxError:
            # exec 실패하면 eval 시도 (표현식일 수 있음)
            pass
        
        # stdout 복원 및 출력 가져오기
        sys.stdout = old_stdout
        printed_output = captured_output.getvalue()
        
        # 결과 수집
        results = []
        
        # 1. print 출력
        if printed_output.strip():
            results.append(printed_output.strip())
        
        # 2. 변수 결과
        if local_vars:
            if "result" in local_vars:
                result_value = local_vars["result"]
            else:
                result_value = local_vars[list(local_vars.keys())[-1]]
            
            results.append(format_result(result_value))
        
        # 3. ⭐ 변수가 없으면 표현식으로 평가
        elif not printed_output.strip():
            try:
                result_value = eval(code, safe_globals, {})
                results.append(format_result(result_value))
            except:
                pass
        
        # 결과 반환
        if results:
            return "\n\n".join(results)
        else:
            return "✅ 실행 완료"
        
    except Exception as e:
        sys.stdout = old_stdout
        
        error_msg = f"❌ 에러: {str(e)}"
        
        if st.session_state.debug_mode:
            with st.expander("🐛 디버그: 에러 상세"):
                st.error(error_msg)
                import traceback
                st.code(traceback.format_exc())
        
        return error_msg

def format_result(result_value):
    """결과를 포맷팅 (PyArrow 에러 방지)"""
    if isinstance(result_value, pd.DataFrame):
        df_str = f"DataFrame ({result_value.shape[0]}행 x {result_value.shape[1]}컬럼)\n"
        df_str += result_value.head(10).to_string()
        return df_str
    elif isinstance(result_value, pd.Series):
        series_str = f"Series (길이 {len(result_value)})\n"
        series_str += result_value.head(10).to_string()
        return series_str
    else:
        return str(result_value)

# ============================================================================
# Part 7: Pending Code 실행 UI
# ============================================================================

if st.session_state.pending_code:
    st.info("💡 Agent가 코드를 제안했습니다.")
    
    with st.expander("🔧 제안된 코드", expanded=True):
        st.code(st.session_state.pending_code, language="python")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ 실행", type="primary", use_container_width=True):
                if st.session_state.df is None:
                    st.error("⚠️ 먼저 CSV 파일을 업로드하세요!")
                else:
                    with st.spinner("실행 중..."):
                        result = safe_exec(
                            st.session_state.pending_code,
                            {"df": st.session_state.df}
                        )
                        
                        st.success("✅ 실행 완료")
                        
                        # 결과 표시
                        with st.container():
                            st.write("**실행 결과:**")
                            if len(result) > 500:
                                with st.expander("📊 결과 보기", expanded=True):
                                    st.text(result)
                            else:
                                st.text(result)
                        
                        # Observation 추가
                        observation_msg = f"Observation: {result}"
                        st.session_state.messages.append(
                            HumanMessage(content=observation_msg)
                        )
                        
                        # Agent에게 다음 행동 요청
                        with st.spinner("Agent 응답 대기..."):
                            response = chat_model.invoke(st.session_state.messages)
                            st.session_state.messages.append(response)
                        
                        st.session_state.pending_code = None
                        st.rerun()
        
        with col2:
            if st.button("✏️ 수정", use_container_width=True):
                modified_code = st.text_area(
                    "코드 수정",
                    value=st.session_state.pending_code,
                    height=150,
                    key="code_edit"
                )
                if st.button("💾 저장", key="save_edit"):
                    st.session_state.pending_code = modified_code
                    st.success("✅ 수정됨")
                    st.rerun()
        
        with col3:
            if st.button("⏭️ 건너뛰기", use_container_width=True):
                st.session_state.messages.append(
                    HumanMessage(content="Observation: (건너뜀)")
                )
                
                with st.spinner("Agent 응답 대기..."):
                    response = chat_model.invoke(st.session_state.messages)
                    st.session_state.messages.append(response)
                
                st.session_state.pending_code = None
                st.rerun()

# ============================================================================
# Part 8: 사용자 입력 처리
# ============================================================================

if user_input := st.chat_input("분석 요청을 입력하세요..."):
    if st.session_state.df is None:
        st.error("⚠️ 먼저 CSV 파일을 업로드하세요!")
        st.stop()
    
    with st.chat_message("user"):
        st.write(user_input)
    
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = chat_model.invoke(st.session_state.messages)
            st.write(response.content)
    
    st.session_state.messages.append(response)
    
    code = extract_code(response.content)
    if code and "Final Answer:" not in response.content:
        st.session_state.pending_code = code
    
    st.rerun()

# ============================================================================
# Part 9: 푸터
# ============================================================================

st.divider()
st.caption("💡 표현식(df.columns), 문장(result = ...), print() 모두 지원합니다!")