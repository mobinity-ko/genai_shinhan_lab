# %% [markdown]
# # Lab 3-4: AI as Partner (Chat & Refactoring)
#
# **학습 목표:**
# 1. AI가 '기억(맥락)'을 가지는 '챗 세션'을 시작합니다.
# 2. AI와 '대화'하며 Pandas 데이터 분석 코드를 점진적으로 '리팩토링'합니다.
#
# **사전 준비:** `sales_data.csv` 파일이 이 스크립트와 같은 폴더에 있는지 확인하세요.

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

# %% [markdown]
# ---
# ### Section 4: AI as Partner (Pandas 리팩토링)

# %%
# === 10. Chat Session 시작 (데이터 분석가 역할 부여) ===

SYSTEM_PROMPT_ANALYST = """
너는 Python Pandas 라이브러리에 매우 능숙한 '시니어 데이터 분석가'이다.
너의 임무는 클린 코드(Clean Code) 원칙에 따라 효율적이고 읽기 쉬운
데이터 분석 코드를 작성하고 리팩토링하는 것이다.
항상 코드 전체를 다시 작성해서 보여줘야 한다.
"""

# (힌트) 'chat_model'과 'chat' 객체 대신, 'chat_history_str'로 맥락을 수동 관리합니다.
# chat_model = ... # 제거
# chat = ... # 제거
chat_history_str = "" # AI와의 대화 맥락을 저장할 변수

print("✅ [Section 4] 'Pandas 전문' AI 파트너(POTENS API)가 준비되었습니다.")


# %%
# === 11. 첫 번째 요청 (Pandas 코드 생성) ===

prompt_chat_1 = """
'pandas' 라이브러리를 사용해서 './data/sales_data.csv' 파일을 읽어온 뒤,
'amount' 컬럼의 '평균(mean)'과 '중앙값(median)'을 계산하여 
딕셔너리 형태로 반환하는 파이썬 함수 `analyze_sales(file_path)`를 생성해줘.
파일이 없을 경우(FileNotFoundError) 예외 처리도 포함해줘.
"""

try:
    print("\n--- [You] (1차 요청: 기본 분석 함수) ---")
    print(prompt_chat_1)
    
    # [YOUR_CODE_HERE_1]
    # (힌트) requests.post(...)를 사용합니다.
    body = {
        "prompt": prompt_chat_1,
        "system_prompt": SYSTEM_PROMPT_ANALYST
    }
    api_response = requests.post(API_URL, headers=HEADERS, json=body)
    api_response.raise_for_status()
    
    response_json = api_response.json()
    response_text = response_json.get('message', 'Error: "message" key not found')
    
    # (NEW) 챗 기록(맥락)을 수동으로 저장
    chat_history_str = f"USER: {prompt_chat_1}\nAI: {response_text}\n"
    
    print("--- [AI 조수] (시니어 분석가) ---")
    print(response_text)
    print("--------------------------------")
    print("\n✅ [성공] AI가 첫 번째 Pandas 코드를 생성했습니다. (이제 이 맥락을 '수동'으로 기억합니다.)")

except Exception as e:
    print(f"🚨 [에러] API 호출 실패: {e}")

# %%
# === 12. 두 번째 요청 (Group By 및 집계 리팩토링) ===
#
# AI가 방금 생성한 코드를 '기억'하고 있으므로,
# "그 코드"라고 지칭하며 'Group By' 같은 복잡한 수정을 요청할 수 있습니다.

# [YOUR_CODE_HERE_2]
# (힌트) "좋아. 방금 네가 준 그 `analyze_sales` 함수를 수정해서..."
prompt_chat_2 = """
좋아. 방금 네가 준 그 `analyze_sales` 함수를 수정해서,
기존 기능은 유지하되, 'category' 컬럼으로 그룹화(group by)한 뒤
각 카테고리별 'amount'의 '총합(sum)'을 계산하는 기능도 추가해줘.

반환값(return)을 2개로 변경해줘.
1. (기존) 평균/중앙값 딕셔너리
2. (신규) 카테고리별 총합 Pandas Series

그리고 Python 타입 힌트(Type Hint)와 Docstring도 완벽하게 추가해줘.
""" 

if "chat_history_str" not in locals() or not chat_history_str: # 1차 요청이 성공했는지 확인
    print("🔔 [알림] '11번' 셀의 1차 요청을 먼저 성공시켜주세요.")
else:
    try:
        print("\n--- [You] (2차 요청: Group By 리팩토링) ---")
        print(prompt_chat_2)
        
        # (NEW) 1차 요청의 맥락(History)을 새 프롬프트에 추가
        full_prompt_chat_2 = chat_history_str + f"USER: {prompt_chat_2}"
        
        # [YOUR_CODE_HERE_3]
        # (힌트) requests.post(...)를 다시 호출합니다. (full_prompt 사용)
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