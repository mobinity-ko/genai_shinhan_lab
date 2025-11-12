"""
핸즈온 랩 3-1: Streamlit 핵심 컴포넌트 익히기
파일명: streamlit_basics.py
실행: streamlit run streamlit_basics.py

소요 시간: 20분
난이도: ⭐⭐

학습 목표:
1. Streamlit 핵심 컴포넌트 실습
2. 레이아웃 구성 방법 이해
3. 상태 관리 (session_state) 체험
4. 빠르게 프로토타입 만들기
"""

import streamlit as st
import pandas as pd
import numpy as np

# ============================================================================
# Part 1: 페이지 설정 및 제목
# ============================================================================

st.set_page_config(
    page_title="Streamlit 컴포넌트 실습",
    page_icon="🎨",
    layout="wide"  # "centered" 또는 "wide"
)

st.title("🎨 Streamlit 핵심 컴포넌트 실습")
st.caption("20분 만에 마스터하는 Streamlit 기초")

# ============================================================================
# Part 2: 텍스트 출력 컴포넌트
# ============================================================================

st.header("📝 Part 1: 텍스트 출력")
st.write("가장 기본적인 출력 방법입니다. Markdown도 지원합니다!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("기본 텍스트")
    st.write("일반 텍스트")
    st.text("고정폭 텍스트 (코드용)")
    st.caption("작은 설명 텍스트")
    
    st.markdown("**굵게**, *기울임*, `코드`")
    st.code("print('Hello World')", language="python")

with col2:
    st.subheader("특수 메시지")
    st.success("✅ 성공 메시지")
    st.info("ℹ️ 정보 메시지")
    st.warning("⚠️ 경고 메시지")
    st.error("❌ 에러 메시지")

st.divider()

# ============================================================================
# Part 3: 입력 컴포넌트
# ============================================================================

st.header("⌨️ Part 2: 사용자 입력")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("텍스트 입력")
    
    # 텍스트 입력
    name = st.text_input("이름을 입력하세요", placeholder="홍길동")
    
    # 숫자 입력
    age = st.number_input("나이", min_value=0, max_value=120, value=30)
    
    # 텍스트 영역
    comment = st.text_area("의견", placeholder="여기에 입력하세요...")

with col2:
    st.subheader("선택 입력")
    
    # 선택 박스
    city = st.selectbox(
        "도시 선택",
        ["서울", "부산", "대구", "인천", "광주"]
    )
    
    # 멀티 셀렉트
    hobbies = st.multiselect(
        "취미 선택 (복수 가능)",
        ["독서", "운동", "영화", "게임", "여행"]
    )
    
    # 라디오 버튼
    gender = st.radio("성별", ["남성", "여성", "기타"])

with col3:
    st.subheader("기타 입력")
    
    # 슬라이더
    satisfaction = st.slider("만족도", 0, 10, 5)
    
    # 체크박스
    agree = st.checkbox("동의합니다")
    
    # 날짜 입력
    date = st.date_input("날짜 선택")
    
    # 시간 입력
    time = st.time_input("시간 선택")

# 입력값 표시
if st.button("입력값 확인", type="primary"):
    st.success("입력값이 저장되었습니다!")
    st.json({
        "이름": name,
        "나이": age,
        "도시": city,
        "취미": hobbies,
        "성별": gender,
        "만족도": satisfaction,
        "동의": agree
    })

st.divider()

# ============================================================================
# Part 4: 데이터 표시 컴포넌트
# ============================================================================

st.header("📊 Part 3: 데이터 표시")

# 샘플 데이터 생성
@st.cache_data  # 데이터 캐싱
def load_sample_data():
    return pd.DataFrame({
        '이름': ['김철수', '이영희', '박민수', '정수진', '최동욱'],
        '나이': [28, 35, 42, 31, 29],
        '부서': ['개발', '마케팅', '기획', '개발', '영업'],
        '연봉': [5000, 4500, 6000, 5200, 4800]
    })

df = load_sample_data()

col1, col2 = st.columns(2)

with col1:
    st.subheader("DataFrame 표시")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Metric 카드")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("평균 나이", f"{df['나이'].mean():.1f}세")
    col_b.metric("평균 연봉", f"{df['연봉'].mean():.0f}만원")
    col_c.metric("총 인원", f"{len(df)}명")

with col2:
    st.subheader("차트")
    
    # 라인 차트
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )
    st.line_chart(chart_data)
    
    # 바 차트
    st.bar_chart(df[['이름', '연봉']].set_index('이름'))

st.divider()

# ============================================================================
# Part 5: 레이아웃 컴포넌트
# ============================================================================

st.header("🎨 Part 4: 레이아웃")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 차트", "📊 데이터", "⚙️ 설정"])

with tab1:
    st.write("차트 탭 내용")
    st.area_chart(chart_data)

with tab2:
    st.write("데이터 탭 내용")
    st.table(df)

with tab3:
    st.write("설정 탭 내용")
    st.slider("설정값", 0, 100, 50)

st.divider()

# Expander
with st.expander("🔽 더 보기 (클릭해서 펼치기)"):
    st.write("숨겨진 내용이 여기 표시됩니다.")
    st.code("""
    # Expander 사용 예시
    with st.expander("제목"):
        st.write("내용")
    """)

st.divider()

# Container
container = st.container(border=True)
container.write("이것은 컨테이너입니다")
container.button("컨테이너 안의 버튼")

st.divider()

# ============================================================================
# Part 6: 사이드바
# ============================================================================

st.header("📌 Part 5: 사이드바")
st.write("왼쪽 사이드바를 확인하세요! →")

with st.sidebar:
    st.title("🎛️ 사이드바")
    st.write("설정이나 네비게이션에 사용")
    
    selected_page = st.radio(
        "페이지 선택",
        ["홈", "데이터", "분석", "설정"]
    )
    
    st.divider()
    
    st.number_input("샘플 크기", 10, 1000, 100)
    
    if st.button("새로고침", use_container_width=True):
        st.rerun()

st.write(f"선택된 페이지: **{selected_page}**")

st.divider()

# ============================================================================
# Part 7: 상태 관리 (session_state)
# ============================================================================

st.header("💾 Part 6: 상태 관리 (중요!)")

st.write("""
Streamlit은 코드가 실행될 때마다 처음부터 다시 실행됩니다.
**session_state**를 사용하면 값을 유지할 수 있습니다!
""")

# 카운터 예제
if "counter" not in st.session_state:
    st.session_state.counter = 0

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ 증가"):
        st.session_state.counter += 1

with col2:
    if st.button("➖ 감소"):
        st.session_state.counter -= 1

with col3:
    if st.button("🔄 초기화"):
        st.session_state.counter = 0

st.metric("현재 카운터 값", st.session_state.counter)

st.divider()

# 리스트 예제
if "items" not in st.session_state:
    st.session_state.items = []

st.subheader("할 일 목록 (To-Do List)")

new_item = st.text_input("할 일 추가", key="todo_input")
if st.button("➕ 추가") and new_item:
    st.session_state.items.append(new_item)
    st.success(f"'{new_item}'이(가) 추가되었습니다!")

if st.session_state.items:
    st.write("**현재 할 일 목록:**")
    for i, item in enumerate(st.session_state.items):
        col1, col2 = st.columns([4, 1])
        col1.write(f"{i+1}. {item}")
        if col2.button("삭제", key=f"delete_{i}"):
            st.session_state.items.pop(i)
            st.rerun()
else:
    st.info("할 일이 없습니다!")

st.divider()

# ============================================================================
# Part 8: 파일 업로드
# ============================================================================

st.header("📁 Part 7: 파일 업로드")

uploaded_file = st.file_uploader(
    "CSV 파일을 업로드하세요",
    type=["csv"],
    help="분석할 CSV 파일을 선택하세요"
)

if uploaded_file is not None:
    df_uploaded = pd.read_csv(uploaded_file)
    
    st.success(f"✅ '{uploaded_file.name}' 파일이 업로드되었습니다!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("행 수", len(df_uploaded))
        st.metric("컬럼 수", len(df_uploaded.columns))
    
    with col2:
        st.write("**컬럼 목록:**")
        st.write(list(df_uploaded.columns))
    
    with st.expander("📊 데이터 미리보기"):
        st.dataframe(df_uploaded.head(10))

st.divider()

# ============================================================================
# Part 9: 진행 상태 표시
# ============================================================================

st.header("⏳ Part 8: 진행 상태")

if st.button("시뮬레이션 실행"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        # 진행 상태 업데이트
        progress_bar.progress(i + 1)
        status_text.text(f"진행 중... {i+1}%")
        
        # 시뮬레이션
        import time
        time.sleep(0.02)
    
    status_text.text("완료! ✅")
    st.balloons()  # 축하 효과!

st.divider()

# ============================================================================
# Part 10: 요약 및 치트시트
# ============================================================================

st.header("📚 Part 9: 치트시트")

with st.expander("🔖 자주 사용하는 컴포넌트"):
    st.code("""
# 텍스트
st.write("anything")
st.title("제목")
st.header("헤더")
st.subheader("서브헤더")
st.markdown("**마크다운**")

# 입력
st.text_input("label")
st.number_input("label", min_value=0, max_value=100)
st.selectbox("label", ["옵션1", "옵션2"])
st.multiselect("label", ["옵션1", "옵션2"])
st.slider("label", 0, 100)
st.checkbox("label")
st.button("label")

# 데이터
st.dataframe(df)
st.table(df)
st.metric("label", value)
st.line_chart(data)
st.bar_chart(data)

# 레이아웃
col1, col2 = st.columns(2)
with col1:
    st.write("컬럼1")
    
tab1, tab2 = st.tabs(["탭1", "탭2"])
with tab1:
    st.write("탭1 내용")
    
with st.expander("펼치기"):
    st.write("숨겨진 내용")
    
with st.sidebar:
    st.write("사이드바")

# 상태 관리
if "key" not in st.session_state:
    st.session_state.key = "value"

# 파일
uploaded_file = st.file_uploader("label", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

# 기타
st.progress(50)
st.spinner("Loading...")
st.success("성공!")
st.error("에러!")
st.balloons()
    """, language="python")

st.divider()

# ============================================================================
# 마무리
# ============================================================================

st.success("🎉 Streamlit 기초 실습 완료!")
st.write("""
**다음 단계:**
- 핸즈온 랩 3-2에서는 이 컴포넌트들을 조합하여
- Pandas Pseudo-Agent와 연동하는 완전한 분석 앱을 만듭니다!
""")

with st.expander("💡 Streamlit 개발 팁"):
    st.markdown("""
    1. **자동 새로고침**: 코드 저장 시 자동으로 앱 새로고침
    2. **디버깅**: `st.write()` 로 어디서나 값 확인 가능
    3. **캐싱**: `@st.cache_data` 로 데이터 로딩 최적화
    4. **레이아웃**: 먼저 종이에 스케치하고 코딩 시작
    5. **session_state**: 사용자 상호작용 시 필수!
    
    **유용한 리소스:**
    - [Streamlit 공식 문서](https://docs.streamlit.io)
    - [Streamlit 갤러리](https://streamlit.io/gallery)
    - [Streamlit Cheat Sheet](https://cheat-sheet.streamlit.app)
    """)

# ============================================================================
# 실행 방법
# ============================================================================
"""
터미널에서 실행:
    streamlit run streamlit_basics.py

주요 단축키:
    - R: 앱 새로고침
    - C: 캐시 지우기
    - Ctrl + C: 서버 종료
"""