# %% [markdown]
# # Lab 2: My First Secure LLM API Call
# 
# **학습 목표:**
# 1. API Key를 코드에 하드코딩하는 '나쁜' 방식의 위험성을 이해합니다.
# 2. `.env` 파일을 사용해 API Key를 '안전하게' 로드하고 API를 호출합니다. (LO 3)
# 3. (핵심) 금융권 현업에서 필수적인 **PII(개인식별정보) 마스킹**을 `presidio` 라이브러리로 처리하고, '안전한' 데이터만 LLM API에 전송합니다. (LO 1)

# %%
# === 1. 기본 설정 ===
# Lab 1에서 설치한 라이브러리들을 불러옵니다.
import os
import requests
# from openai import OpenAI  # 또는 Anthropic, Google Gemini

print("라이브러리 로드 완료!")

# %%
# === 2. .env 파일 로드 ===
# os.getenv()를 사용해 환경 변수로 로드된 Key를 가져옵니다.
API_KEY = os.getenv("POTENS_API_KEY") # 또는 사용할 LLM에 맞게 변경
if not API_KEY:
    print("🚨 [에러] .env 파일에서 API Key를 로드하세요.")

#%%
# === 3. API 호출 테스트 ===
API_URL = "https://ai.potens.ai/api/chat"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
body = {
    "prompt": "신한카드가 GenAI 교육을 하는 이유에 대해 한 문장으로 요약해줘.",
    # "system_prompt": "너는 고양이야. 고양이처럼 대답해줘"
}
try:
    response = requests.post(API_URL, headers=headers, json=body)
    response.raise_for_status() # 오류가 있으면 예외 발생

    api_response = response.json()
    print(f"API 응답: {api_response['message']}")
    print("\n✅ [성공] requests로 API가 성공적으로 호출되었습니다.")

except Exception as e:
    print(f"🚨 [에러] API 호출에 실패했습니다: {e}")