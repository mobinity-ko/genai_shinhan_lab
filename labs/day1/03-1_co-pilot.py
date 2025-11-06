# %% [markdown]
# # Lab 3-1: AI as Co-Pilot
#
# **학습 목표:**
# 1. AI 조수에게 데이터 분석가에게 필요한 코드(정규식, SQL, 시각화) 생성을 요청합니다.
#
# %%
# === 1. 기본 설정 (LLM API 호출 세팅) ===
import os
import requests  
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

# === POTENS API 호출 헬퍼 함수 ===
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
# === 2. 정규식(Regex) 생성 요청 ===
print("\n--- [1. 정규식(Regex) 생성 요청] ---")
prompt_regex = """
[프롬프트를 입력하세요]
"2023-10-27 10:30:01,ERROR,192.168.1.10,PaymentFailed,User=123"


"""

try:
    response_text = call_potens_api(prompt_regex)
    
    print("--- [AI가 생성한 Python 정규식 코드] ---")
    print(response_text)

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")

# %%
# === 생성된 코드 실행 ===

# %%
# === 3. SQL 쿼리 생성 요청 ===
print("\n--- [2. SQL 쿼리 생성 요청] ---")
prompt_sql = """
[프롬프트를 입력하세요]

"""

try:
    response_text = call_potens_api(prompt_sql)
    
    print("--- [AI가 생성한 SQL 쿼리] ---")
    print(response_text)

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")

# %%
# === 생성된 코드 실행 ===
# (실제 DB 연결 및 실행은 생략)

# %%
# === 4. (NEW) 데이터 시각화 코드 생성 ===
print("\n--- [3. 데이터 시각화 코드 생성 요청] ---")
prompt_viz = """
[프롬프트를 입력하세요]

"""

try:
    response_text = call_potens_api(prompt_viz)
    
    print("--- [AI가 생성한 Matplotlib 시각화 코드] ---")
    print(response_text)

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")
# %%
# === 생성된 코드 실행 ===
