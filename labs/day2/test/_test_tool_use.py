#%%
# === 1. 기본 설정 (API 헬퍼 함수) ===
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POTENS_API_KEY")
API_URL = "https://ai.potens.ai/api/chat"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_potens_api_for_tool_use(prompt, system_prompt=None, tools=None):
    """
    (수정) 'tools' 파라미터를 API body에 포함시킬 수 있도록 
    수정된 API 헬퍼 함수입니다.
    """
    body = {"prompt": prompt}
    if system_prompt:
        body["system_prompt"] = system_prompt
    
    # (핵심) 만약 tools가 있다면, API body에 추가합니다.
    # (참고) Potens API가 'tools'가 아닌 'tool_definitions' 등 
    # 다른 key를 사용할 수도 있습니다. (개발 부서 확인 필요)
    if tools:
        body["tools"] = tools 
    
    print("--- 🚀 API Request (Tool Use Test) ---")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print("-----------------------------------")
    
    response = requests.post(API_URL, headers=HEADERS, json=body, timeout=60)
    response.raise_for_status() 
    
    # Tool Use 응답은 JSON 객체 전체를 반환할 가능성이 높습니다.
    return response.json() 

#%%
# === 2. Tool Use 성능 테스트 ===

# (핵심) Agent가 LLM에게 보낼 '도구 명세서'입니다.
# "python_repl"이라는 도구가 있고, "query"라는 문자열 인자가 필요하다고 정의
tools_definition = [
    {
        "name": "python_repl",
        "description": "pandas DataFrame(df)에 대해 Python 코드를 실행하는 도구.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "실행할 Python 코드. (예: df.head())"
                }
            },
            "required": ["query"]
        }
    }
]

# 사용자 질문
user_prompt = "데이터(df)의 첫 5줄을 보여줘."


# === 3. API 호출 및 결과 확인 ===
print("🚀 Tool Use 포맷 테스트 시작...")

try:
    api_response = call_potens_api_for_tool_use(
        user_prompt, 
        tools=tools_definition
    )
    
    print("\n--- 🤖 API Response (Raw JSON) ---")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    print("---------------------------------")

    # === 4. 결과 분석 ===
    
    # (가정) Potens API가 Anthropic 표준을 따른다면,
    # 'message'가 아닌 'content' 블록에 'tool_use' 타입이 반환될 수 있습니다.
    # 이 부분은 실제 반환되는 JSON을 보고 확인해야 합니다.
    
    if "message" in api_response and isinstance(api_response["message"], str):
        print("\n❌ [실패] API가 'tools' 명세를 무시하고 일반 텍스트 메시지를 반환했습니다.")
        print(f"   (응답: {api_response['message']})")
        print("   (ReAct 방식으로만 작동하는 것으로 보입니다.)")
    
    # (가정) 성공 시 응답이 이런 구조일 수 있습니다 (Anthropic Claude 기준)
    # { "content": [ ..., { "type": "tool_use", "name": "python_repl", ... } ] }
    elif "content" in api_response and "tool_use" in str(api_response["content"]):
        print("\n✅ [성공] LLM이 'Tool Use'를 이해하고 구조화된 응답을 반환했습니다!")
        print("   (LangChain 'Tool Use' Agent 연동이 가능합니다.)")
    
    else:
        print("\n⚠️ [알 수 없음] 반환된 JSON 구조를 확인하세요.")
        print("   ('message' 키가 텍스트가 아니거나, 'content' 키가 없습니다.)")


except requests.HTTPError as e:
    if e.response.status_code == 400:
        print(f"\n❌ [실패] API가 'tools' 파라미터를 인식하지 못하고 400 Bad Request 오류를 반환했습니다.")
        print("   (API가 Tool Use를 지원하지 않는 엔드포인트일 수 있습니다.)")
    else:
        print(f"\n❌ [실패] API 호출 중 오류 발생: {e}")
# %%
