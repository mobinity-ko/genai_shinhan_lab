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