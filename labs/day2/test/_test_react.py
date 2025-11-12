#%%
# === 1. 기본 설정 (기존 코드 활용) ===
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POTENS_API_KEY")
API_URL = "https://ai.potens.ai/api/chat"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_potens_api(prompt, system_prompt=None):
    """POTENS API를 호출하는 헬퍼 함수"""
    body = {"prompt": prompt}
    if system_prompt:
        body["system_prompt"] = system_prompt
    
    print("--- 🚀 API Request ---")
    print(f"[System]: {system_prompt}")
    print(f"[Prompt]: {prompt}")
    print("----------------------")
    
    response = requests.post(API_URL, headers=HEADERS, json=body)
    response.raise_for_status() 
    
    api_response = response.json()
    return api_response.get('message', 'Error: "message" key not found')

#%%
# === 2. ReAct 성능 테스트 ===

# (핵심) ReAct Agent가 LLM에게 보내는 프롬프트의 '축소판'입니다.
# LLM에게 "어떤 도구가 있는지", "어떤 형식으로 답해야 하는지" 명시적으로 지시합니다.
system_prompt_for_react = """
당신은 Python 코드를 실행할 수 있는 AI 어시스턴트입니다.
당신은 'python_repl'이라는 도구(tool) 하나만 사용할 수 있습니다.

질문에 답하기 위해, 당신은 **반드시** 다음 포맷 중 하나로만 대답해야 합니다.

**포맷 1 (생각 및 행동):**
Thought: [질문을 해결하기 위한 당신의 생각과 계획]
Action: [사용할 도구 이름, 여기서는 'python_repl'만 가능]
Action Input: [해당 도구에 입력할 Python 코드]

**포맷 2 (최종 답변):**
Thought: [최종 답변을 도출한 과정]
Final Answer: [사용자에게 전달할 최종 답변]
"""

# 사용자 질문
user_prompt = "간단하게 'Hello World'를 출력하는 파이썬 코드를 실행해줘."


# === 3. API 호출 및 결과 확인 ===
print("🚀 ReAct 포맷 테스트 시작...")
raw_response = call_potens_api(user_prompt, system_prompt_for_react)

print("\n--- 🤖 API Response (Raw) ---")
print(raw_response)
print("----------------------------")

# === 4. 결과 분석 ===
if "Action:" in raw_response and "python_repl" in raw_response:
    print("\n✅ [성공] LLM이 ReAct 포맷 (Thought/Action)을 이해하고 생성했습니다.")
else:
    print("\n❌ [실패] LLM이 ReAct 포맷을 따르지 않고, 일반적인 대답을 반환했습니다.")
    print("    (Agent가 'OutputParserException'을 일으킬 가능성이 높습니다.)")
# %%
