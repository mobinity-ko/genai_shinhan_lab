# %% [markdown]
# # Lab 3-1: AI as Co-Pilot
#
# **학습 목표:**
# 1. AI 조수에게 데이터 분석가에게 필요한 코드(정규식, SQL, 시각화) 생성을 요청합니다.
#
# 💡 **CLI Warm-up:** `gemini "Python pandas로 CSV 파일 읽어서 'Age' 컬럼 평균 구하는 코드 짜줘"`

# %%
# === 1. 기본 설정 ===
import os
import requests  # 'google.generativeai' 대신 'requests' 임포트
from dotenv import load_dotenv

# .env 파일에서 API Key 로드
load_dotenv()
API_KEY = os.getenv("POTENS_API_KEY")

if not API_KEY:
    print("🚨 [에러] .env 파일에서 API Key를 로드하세요.")
else:
    # POTENS API 설정
    API_URL = "https://ai.potens.ai/api/chat"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    print("✅ POTENS API 클라이언트 설정 완료.")

# === (NEW) POTENS API 호출 헬퍼 함수 ===
def call_potens_api(prompt, system_prompt=None):
    """POTENS API를 호출하는 헬퍼 함수"""
    body = {"prompt": prompt}
    if system_prompt:
        body["system_prompt"] = system_prompt
    
    response = requests.post(API_URL, headers=HEADERS, json=body)
    response.raise_for_status() # 오류가 있으면 예외 발생
    
    api_response = response.json()
    return api_response.get('message', 'Error: "message" key not found')

# %% [markdown]
# ---
# ### Section 1: AI as Co-Pilot (데이터 분석가를 위한 코드 생성)

# %%
# === 2. (NEW) 정규식(Regex) 생성 요청 ===
print("\n--- [1. 정규식(Regex) 생성 요청] ---")
prompt_regex = """
'log_data.txt' 파일에 아래와 같은 로그가 수백 줄 있습니다.
"2023-10-27 10:30:01,ERROR,192.168.1.10,PaymentFailed,User=123"

이 텍스트에서 '날짜' (YYYY-MM-DD), '로그 레벨' (ERROR, INFO 등), 'IP 주소'
3가지 정보를 추출하는 Python 정규식(regex) 코드를 작성해줘.
re.findall()을 사용하는 예시 코드로 보여줘.
"""

try:
    # [YOUR_CODE_HERE] -> POTENS API 호출로 변경
    response_text = call_potens_api(prompt_regex)
    
    print("--- [AI가 생성한 Python 정규식 코드] ---")
    print(response_text)
    print("---------------------------------------")

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")

# %%
# === 3. SQL 쿼리 생성 요청 ===
print("\n--- [2. SQL 쿼리 생성 요청] ---")
prompt_sql = """
테이블 'CARD_TRANSACTIONS' (컬럼: user_id, amount, merchant_name, transaction_date)에서
'merchant_name'이 '스타벅스'이면서 'amount'가 10000원 이상인
'user_id'를 'transaction_date' 기준으로 최신순 정렬(DESC)하여
중복 없이 10개만 조회하는 SQL 쿼리를 생성해줘.
"""

try:
    # [YOUR_CODE_HERE] -> POTENS API 호출로 변경
    response_text = call_potens_api(prompt_sql)
    
    print("--- [AI가 생성한 SQL 쿼리] ---")
    print(response_text)
    print("-------------------------------")

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")

# %%
# === 4. (NEW) 데이터 시각화 코드 생성 ===
print("\n--- [3. 데이터 시각화 코드 생성 요청] ---")
prompt_viz = """
Python의 'matplotlib' 라이브러리를 사용해서,
아래 딕셔너리 데이터를 'Bar Chart'(막대 그래프)로 그리는 코드를 생성해줘.

data = {'스타벅스': 120, '이마트': 85, '신세계백화점': 40}

- X축은 key (매장명), Y축은 value (방문 횟수)
- 차트 제목(Title)은 '매장별 방문 횟수'
- X축, Y축 레이블(Label) 설정
- 한글 폰트가 깨지지 않도록 설정하는 코드 포함
"""

try:
    # [YOUR_CODE_HERE] -> POTENS API 호출로 변경
    response_text = call_potens_api(prompt_viz)
    
    print("--- [AI가 생성한 Matplotlib 시각화 코드] ---")
    print(response_text)

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")
# %%
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 한글 폰트 설정 (Windows, Mac, Linux 환경별 대응)
import platform

system = platform.system()

if system == 'Windows':
    # Windows 환경
    font_name = font_manager.FontProperties(fname='c:/Windows/Fonts/malgun.ttf').get_name()
    rc('font', family=font_name)
elif system == 'Darwin':  # Mac
    rc('font', family='AppleGothic')
else:  # Linux
    rc('font', family='NanumGothic')

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# 데이터
data = {'스타벅스': 120, '이마트': 85, '신세계백화점': 40}

# 데이터 분리
stores = list(data.keys())
visits = list(data.values())

# 막대 그래프 생성
plt.figure(figsize=(10, 6))
plt.bar(stores, visits, color='skyblue', edgecolor='navy', alpha=0.7)

# 제목 및 레이블 설정
plt.title('매장별 방문 횟수', fontsize=16, fontweight='bold')
plt.xlabel('매장명', fontsize=12)
plt.ylabel('방문 횟수', fontsize=12)

# 그리드 추가 (선택사항)
plt.grid(axis='y', linestyle='--', alpha=0.3)

# 그래프 표시
plt.tight_layout()
plt.show()
# %%
