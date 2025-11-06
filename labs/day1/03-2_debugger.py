# %% [markdown]
# # Lab 3-2: AI as Debugger
#
# **학습 목표:**
# 1. AI에게 '에러 코드'와 '에러 로그'라는 '맥락(Context)'을 주어 해결책을 찾습니다.
#
# 💡 **CLI Warm-up:** 터미널에서 `cat buggy_code.py | gemini "이 코드 버그 다 찾아서 고쳐줘"`를 실행해보세요.

# %%
# === 1. 기본 설정 ===
import os
import requests  # 'google.generativeai' 대신 'requests' 임포트
from dotenv import load_dotenv

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
# ### Section 2: AI as Debugger (Debugging)

# %%
# === 5. 버그가 있는 코드 로드 ===
# (사전 제공된 'buggy_code.py' 파일)
try:
    with open('./data/buggy_code.py', 'r', encoding='utf-8') as f:
        buggy_code = f.read()
    print("--- [버그가 있는 원본 코드] ---")
    print(buggy_code)
    print("----------------------------")
except FileNotFoundError:
    print("🚨 [에러] 'buggy_code.py' 파일을 찾을 수 없습니다.")
    buggy_code = ""

# %%
# === 6. AI에게 디버깅 요청 ===
prompt_debug = f"""
아래 파이썬 코드를 실행하면 에러가 발생해.
이 코드의 모든 잠재적인 버그(최소 3개)를 찾아서 원인을 설명하고,
모든 버그가 수정된 전체 코드를 다시 작성해줘.

--- [버그 코드] ---
{buggy_code}
--- [버그 코드 끝] ---
"""

# [YOUR_CODE_HERE_1]
if buggy_code:
    try:
        print("\n⏳ AI가 디버깅 리포트를 생성 중입니다...")
        
        # [YOUR_CODE_HERE_1] -> POTENS API 호출로 변경
        response_text = call_potens_api(prompt_debug)
        
        print("--- [AI의 디버깅 리포트] ---")
        print(response_text)
        print("----------------------------")
        print("\n✅ [성공] '02_debugger.py' 완료. (학습 목표 2 달성!)")
        print("➡️ '03_guardrails.py' 파일을 열어 다음 실습을 진행하세요.")

    except Exception as e:
        print(f"🚨 [에러] API 호출 실패: {e}")
# %%
