# %% [markdown]
# # Lab 3-3: AI as Partner (Chat & Refactoring)
#
# **학습 목표:**
# 1. AI가 '기억(맥락)'을 가지는 '챗 세션'을 시작합니다.
# 2. AI와 '대화'하며 Pandas 데이터 분석 코드를 점진적으로 '리팩토링'합니다.
# %%
# === 기본 설정 (LLM API 호출 세팅) ===
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
# %%
# === 1. Chat Session 시작 (데이터 분석가 역할 부여) ===

SYSTEM_PROMPT_ANALYST = """
[시스템 프롬프트를 입력하세요]

"""

# 'chat_history_str'로 맥락을 수동 관리합니다.
chat_history_str = "" # AI와의 대화 맥락을 저장할 변수

print("✅ [Section 4] 'Pandas 전문' AI 파트너(POTENS API)가 준비되었습니다.")


# %%
# === 2. 첫 번째 요청 (Pandas 코드 생성) ===

prompt_chat_1 = """
[프롬프트1을 입력하세요]

"""

try:
    print("\n--- [You] (1차 요청: 기본 분석 함수) ---")
    print(prompt_chat_1)
    
    body = {
        "prompt": prompt_chat_1,
        "system_prompt": SYSTEM_PROMPT_ANALYST
    }
    api_response = requests.post(API_URL, headers=HEADERS, json=body)
    api_response.raise_for_status()
    
    response_json = api_response.json()
    response_text = response_json.get('message', 'Error: "message" key not found')
    
    # (중요!) 챗 기록(맥락)을 수동으로 저장
    chat_history_str = f"USER: {prompt_chat_1}\nAI: {response_text}\n"
    
    print("--- [AI 조수] (시니어 분석가) ---")
    print(response_text)
    print("--------------------------------")
    print("\n✅ [성공] AI가 첫 번째 Pandas 코드를 생성했습니다. (이제 이 맥락을 '수동'으로 기억합니다.)")

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")

# %%
# === 3. 두 번째 요청 (Group By 및 집계 리팩토링) ===

prompt_chat_2 = """
[프롬프트2를 입력하세요]

""" 

if "chat_history_str" not in locals() or not chat_history_str: # 1차 요청이 성공했는지 확인
    print("🔔 [알림] '11번' 셀의 1차 요청을 먼저 성공시켜주세요.")
else:
    try:
        print("\n--- [You] (2차 요청: Group By 리팩토링) ---")
        print(prompt_chat_2)
        
        # (중요!) 1차 요청의 맥락(History)을 새 프롬프트에 추가
        full_prompt_chat_2 = chat_history_str + f"USER: {prompt_chat_2}"

        body = {
            "prompt": full_prompt_chat_2,
            "system_prompt": SYSTEM_PROMPT_ANALYST
        }
        api_response = requests.post(API_URL, headers=HEADERS, json=body)
        api_response.raise_for_status()
        
        response_json = api_response.json()
        response_text = response_json.get('message', 'Error: "message" key not found')
        
        print("--- [AI 조수] (리팩토링) ---")
        print(response_text)
        print("---------------------------")
        print("\n✅ [성공] AI가 이전 맥락을 기억하고 Pandas 코드를 '리팩토링'했습니다! (학습 목표 4 달성!)")


    except Exception as e:
        print(f"🚨 [에러] API 호출 실패: {e}")
# %%
# === 생성된 코드 실행 ===
