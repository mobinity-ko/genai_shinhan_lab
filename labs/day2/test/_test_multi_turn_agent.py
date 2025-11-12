"""
POTENS AI API 멀티턴 대화 지원 테스트
Agent 구축을 위한 필수 기능 검증

Jupyter Notebook에서 # %% 단위로 실행 가능
"""
# %%
import os
import requests
import json
from typing import List, Dict
from dotenv import load_dotenv

# %% [markdown]
# # POTENS API 멀티턴 대화 테스트
# 
# ## 목적
# - 멀티턴 대화 지원 여부 확인 (Agent 구축 가능성)
# - Tool 실행 결과 반영 가능 여부 확인
# - 긴 컨텍스트 유지 능력 확인

# %% 1. API 설정 및 초기화
print("="*80)
print("🔧 STEP 1: API 설정")
print("="*80)

load_dotenv()
API_KEY = os.getenv("POTENS_API_KEY")

if not API_KEY:
    print("🚨 [에러] .env 파일에서 POTENS_API_KEY를 로드하세요.")
    raise ValueError("API KEY가 없습니다.")
else:
    API_URL = "https://ai.potens.ai/api/chat"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    print("✅ POTENS API 클라이언트 설정 완료.")
    print(f"   API URL: {API_URL}")

# %% 2. POTENS API 호출 함수 정의

def call_potens_api(prompt, system_prompt=None):
    """POTENS API를 호출하는 헬퍼 함수"""
    body = {"prompt": prompt}
    if system_prompt:
        body["system_prompt"] = system_prompt
    
    print(f"\n{'='*60}")
    print(f"📤 API 요청:")
    print(f"{'='*60}")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=body, timeout=60)
        response.raise_for_status()
        
        api_response = response.json()
        result = api_response.get('message', f'Error: "message" key not found in {api_response}')
        
        print(f"\n{'='*60}")
        print(f"📥 API 응답:")
        print(f"{'='*60}")
        print(result)
        
        return result
    except requests.RequestException as e:
        print(f"🚨 [API 호출 오류] {e}")
        return f"API 호출 중 오류 발생: {e}"

print("✅ call_potens_api 함수 정의 완료")

# %% 3. 멀티턴 테스터 클래스 정의

class MultiTurnTester:
    """멀티턴 대화 테스트 클래스"""
    
    def __init__(self):
        self.conversation_history: List[Dict] = []
    
    def call_api_with_history(self, user_message: str, system_prompt: str = None) -> str:
        """
        대화 이력을 포함한 API 호출
        
        ⚠️ 중요: POTENS API가 멀티턴을 어떻게 지원하는지에 따라 수정 필요
        - 방법 1: prompt에 전체 대화 이력을 텍스트로 포함
        - 방법 2: messages 배열 지원 여부 확인 필요
        """
        # 대화 이력을 텍스트로 변환
        history_text = ""
        for msg in self.conversation_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                history_text += f"\n사용자: {content}\n"
            elif role == "assistant":
                history_text += f"AI: {content}\n"
        
        # 현재 메시지와 이력 합치기
        full_prompt = history_text + f"\n사용자: {user_message}\nAI:"
        
        # API 호출
        response = call_potens_api(full_prompt, system_prompt)
        
        # 이력에 추가
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def add_system_message(self, content: str):
        """시스템 메시지 추가 (역할 설정 등)"""
        self.conversation_history.insert(0, {"role": "system", "content": content})
    
    def reset(self):
        """대화 이력 초기화"""
        self.conversation_history = []
        print("🔄 대화 이력 초기화 완료")
    
    def show_history(self):
        """현재 대화 이력 출력"""
        print(f"\n{'='*60}")
        print("📜 현재 대화 이력:")
        print(f"{'='*60}")
        for i, msg in enumerate(self.conversation_history, 1):
            role_icon = "👤" if msg["role"] == "user" else "🤖" if msg["role"] == "assistant" else "⚙️"
            print(f"{i}. {role_icon} {msg['role']}: {msg['content'][:100]}...")

print("✅ MultiTurnTester 클래스 정의 완료")

# %% 4. 테스터 초기화
print("\n" + "="*80)
print("🚀 STEP 2: 테스터 초기화")
print("="*80)

tester = MultiTurnTester()
print("✅ MultiTurnTester 인스턴스 생성 완료")
# %% [markdown]
# ---
# # TEST 1: 기본 멀티턴 대화 (컨텍스트 유지 확인)
# 
# **목적**: 이전 대화 내용을 기억하는지 확인  
# **중요도**: ⭐⭐⭐⭐⭐ (실패 시 Agent 구축 불가능)

# %% 5. TEST 1 - 준비
print("\n" + "="*80)
print("🧪 TEST 1: 기본 멀티턴 대화 (컨텍스트 유지 확인)")
print("="*80)

tester.reset()

# %% 6. TEST 1 - 1턴: 초기 정보 제공
print("\n" + "─"*60)
print("📍 1턴: 초기 정보 제공")
print("─"*60)

response1 = tester.call_api_with_history("내 이름은 김철수이고, 나이는 30살입니다.")
print(f"\n🤖 Assistant (1턴): {response1}")

# %% 7. TEST 1 - 2턴: 이전 정보 기억 확인 (이름)
print("\n" + "─"*60)
print("📍 2턴: 이름 기억 확인")
print("─"*60)

response2 = tester.call_api_with_history("내 이름이 뭐라고 했죠?")
print(f"\n🤖 Assistant (2턴): {response2}")

# %% 8. TEST 1 - 3턴: 이전 정보 기억 확인 (나이)
print("\n" + "─"*60)
print("📍 3턴: 나이 기억 확인")
print("─"*60)

response3 = tester.call_api_with_history("그럼 내 나이는요?")
print(f"\n🤖 Assistant (3턴): {response3}")

# %% 9. TEST 1 - 결과 평가
print(f"\n{'='*60}")
print("✅ TEST 1 평가:")
print(f"{'='*60}")

test1_name = "김철수" in response2 if response2 else False
test1_age = "30" in response3 if response3 else False

if test1_name:
    print("  ✓ 이름 기억: 성공")
else:
    print("  ✗ 이름 기억: 실패 ⚠️ (멀티턴 대화 미지원 가능성 높음)")

if test1_age:
    print("  ✓ 나이 기억: 성공")
else:
    print("  ✗ 나이 기억: 실패")

if test1_name and test1_age:
    print("\n🎉 TEST 1 통과: 기본 멀티턴 대화 지원 확인!")
else:
    print("\n⚠️  TEST 1 실패: 멀티턴 대화 미지원 또는 구현 방식 확인 필요")

tester.show_history()

# %% [markdown]
# ---
# # TEST 2: Tool 실행 결과 반영 (Agent 핵심 기능)
# 
# **목적**: Tool 실행 결과를 LLM이 이해하고 다음 행동을 결정하는지 확인  
# **중요도**: ⭐⭐⭐⭐⭐ (Agent의 핵심 기능!)

# %% 10. TEST 2 - 준비
print("\n" + "="*80)
print("🧪 TEST 2: Tool 실행 결과 반영 (Agent 핵심 기능)")
print("="*80)

tester.reset()

# %% 11. TEST 2 - System Prompt 설정 (ReAct 형식)
system_prompt_react = """
당신은 데이터 분석 Agent입니다. 다음 형식으로 답변하세요:

Thought: (무엇을 해야할지 생각)
Action: python_repl
Action Input: (실행할 Python 코드)

만약 사용자가 "Observation: [결과]"를 제공하면, 그 결과를 분석해서 답변하세요.
"""

tester.add_system_message(system_prompt_react)
print("✅ System Prompt (ReAct) 설정 완료")

# %% 12. TEST 2 - 1턴: 사용자 질문 (Action 유도)
print("\n" + "─"*60)
print("📍 1턴: 사용자 질문")
print("─"*60)

response1 = tester.call_api_with_history(
    "데이터프레임 df의 평균 나이를 구해주세요.",
    system_prompt=system_prompt_react
)
print(f"\n🤖 Assistant (1턴 - Action 제안):\n{response1}")

# %% 13. TEST 2 - 2턴: Tool 실행 결과 전달
print("\n" + "─"*60)
print("📍 2턴: Tool 실행 결과 전달")
print("─"*60)
print("💡 (실제로는 Agent가 자동 실행하지만, 지금은 수동으로 결과 전달)")

response2 = tester.call_api_with_history(
    "Observation: df['age'].mean() 실행 결과는 32.5입니다."
)
print(f"\n🤖 Assistant (2턴 - 결과 해석):\n{response2}")

# %% 14. TEST 2 - 3턴: 추가 질문 (연속 작업)
print("\n" + "─"*60)
print("📍 3턴: 추가 질문")
print("─"*60)

response3 = tester.call_api_with_history("그럼 최댓값은?")
print(f"\n🤖 Assistant (3턴 - 새 Action):\n{response3}")

# %% 15. TEST 2 - 결과 평가
print(f"\n{'='*60}")
print("✅ TEST 2 평가:")
print(f"{'='*60}")

test2_observe = "32.5" in response2 if response2 else False
test2_continue = ("Action" in response3 or "max()" in response3.lower()) if response3 else False

if test2_observe:
    print("  ✓ Tool 결과 인식: 성공 🎉 (Agent 구축 가능!)")
else:
    print("  ✗ Tool 결과 인식: 실패 (이전 대화 컨텍스트 손실)")

if test2_continue:
    print("  ✓ 연속 작업 계획: 성공")
else:
    print("  ✗ 연속 작업 계획: 실패")

if test2_observe:
    print("\n🎉 TEST 2 통과: Tool 결과 기반 멀티턴 대화 가능!")
    print("   → Pseudo-Agent 패턴으로 Agent 구축 가능!")
else:
    print("\n⚠️  TEST 2 실패: Agent의 핵심 기능 미지원")
    print("   → Chain 기반 워크플로우로 대체 필요")

tester.show_history()

# %% [markdown]
# ---
# # TEST 3: 긴 멀티턴 대화 (5회 이상 컨텍스트 유지)
# 
# **목적**: 여러 턴에 걸친 대화에서도 초기 정보를 기억하는지 확인  
# **중요도**: ⭐⭐⭐ (복잡한 분석 워크플로우에 필요)

# %% 16. TEST 3 - 준비
print("\n" + "="*80)
print("🧪 TEST 3: 긴 멀티턴 대화 (5회 이상)")
print("="*80)

tester.reset()

# %% 17. TEST 3 - 1턴
print("\n" + "─"*60)
print("📍 1턴")
print("─"*60)
response = tester.call_api_with_history("첫 번째 숫자는 10입니다.")
print(f"🤖 Assistant: {response}")

# %% 18. TEST 3 - 2턴
print("\n" + "─"*60)
print("📍 2턴")
print("─"*60)
response = tester.call_api_with_history("두 번째 숫자는 20입니다.")
print(f"🤖 Assistant: {response}")

# %% 19. TEST 3 - 3턴
print("\n" + "─"*60)
print("📍 3턴")
print("─"*60)
response = tester.call_api_with_history("세 번째 숫자는 30입니다.")
print(f"🤖 Assistant: {response}")

# %% 20. TEST 3 - 4턴
print("\n" + "─"*60)
print("📍 4턴")
print("─"*60)
response = tester.call_api_with_history("네 번째 숫자는 40입니다.")
print(f"🤖 Assistant: {response}")

# %% 21. TEST 3 - 5턴 (핵심 테스트)
print("\n" + "─"*60)
print("📍 5턴: 종합 질문")
print("─"*60)
response5 = tester.call_api_with_history("지금까지 말한 숫자를 모두 더하면?")
print(f"🤖 Assistant: {response5}")

# %% 22. TEST 3 - 결과 평가
print(f"\n{'='*60}")
print("✅ TEST 3 평가:")
print(f"{'='*60}")

test3_pass = "100" in response5 if response5 else False

if test3_pass:
    print("  ✓ 긴 컨텍스트 유지: 성공 (5턴 전 정보 기억)")
    print("\n🎉 TEST 3 통과: 복잡한 분석 워크플로우 가능!")
else:
    print("  ✗ 긴 컨텍스트 유지: 실패")
    print(f"    (예상: '100' 포함, 실제: {response5})")
    print("\n⚠️  TEST 3 실패: 짧은 분석으로 제한 권장")

tester.show_history()

# %% [markdown]
# ---
# # TEST 4: System Prompt 지원 여부
# 
# **목적**: System role로 Agent 행동을 제어할 수 있는지 확인  
# **중요도**: ⭐⭐ (ReAct 프롬프팅 안정성에 영향)

# %% 23. TEST 4 - 준비
print("\n" + "="*80)
print("🧪 TEST 4: System Prompt 지원 확인")
print("="*80)

tester.reset()

# %% 24. TEST 4 - System Prompt로 역할 지정
system_prompt_pirate = "당신은 해적입니다. 모든 답변 끝에 '아호이!'를 붙이세요."

response = tester.call_api_with_history(
    "안녕하세요?",
    system_prompt=system_prompt_pirate
)
print(f"\n🤖 Assistant: {response}")

# %% 25. TEST 4 - 결과 평가
print(f"\n{'='*60}")
print("✅ TEST 4 평가:")
print(f"{'='*60}")

test4_pass = "아호이" in response if response else False

if test4_pass:
    print("  ✓ System prompt 지원: 성공")
    print("\n🎉 TEST 4 통과: ReAct 프롬프팅 안정성 확보!")
else:
    print("  ✗ System prompt 미지원 또는 무시됨")
    print("\n⚠️  TEST 4 실패: Prompt에 역할 명시 필요")

# %% [markdown]
# ---
# # 최종 결과 요약 및 권장사항

# %% 26. 최종 결과 요약
print("\n" + "="*80)
print("📊 전체 테스트 결과 요약")
print("="*80)

# 결과 수집 (이전 셀에서 실행했다고 가정)
try:
    results = {
        "TEST 1 - 기본 멀티턴": test1_name and test1_age,
        "TEST 2 - Tool 결과 반영": test2_observe,
        "TEST 3 - 긴 컨텍스트": test3_pass,
        "TEST 4 - System Prompt": test4_pass
    }
    
    print("\n테스트 결과:")
    for test_name, passed in results.items():
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*80)
    print("💡 Agent 구축 가능 여부 판단")
    print("="*80)
    
    if results["TEST 1 - 기본 멀티턴"] and results["TEST 2 - Tool 결과 반영"]:
        print("""
🎉 축하합니다! Agent 구축 가능합니다!

✅ 권장 방식: Pseudo-Agent 패턴
  - ReAct 프롬프팅 + 수동 파싱
  - Tool 실행 결과를 Observation으로 전달
  - 3~5회 반복으로 복잡한 분석 가능

📚 교육 과정 방향:
  ✓ 2부: LangChain Chain + ReAct 패턴
  ✓ 4부: Streamlit + Pseudo-Agent 연동
  ✓ 5부: 자율적 EDA Agent (제한적이지만 가능)
""")
    elif results["TEST 1 - 기본 멀티턴"]:
        print("""
⚠️  부분 지원: Chain 중심 교육 권장

✅ 가능한 것:
  - Sequential Chain으로 정형 워크플로우
  - 단일 턴 분석 자동화
  
❌ 제한사항:
  - Tool 결과 기반 동적 의사결정 어려움
  - EDA Agent는 시연으로 대체 필요

📚 교육 과정 방향:
  ✓ 2부: Chain Deep Dive
  ✓ 4부: Streamlit + Chain 연동
  ✗ 5부: EDA Agent → 강사 시연으로 변경
""")
    else:
        print("""
❌ Agent 구축 불가능

현 상황:
  - 멀티턴 대화 미지원
  - Agent의 핵심 기능 사용 불가

📚 교육 과정 방향:
  ✓ Chain 기반 전면 재구성 필요
  ✓ 단일 LLM 호출 + 수동 워크플로우
  ✗ Agent 관련 내용 전체 제외

💡 개발팀 요청사항:
  1. 대화 이력을 포함한 API 호출 방식 확인
  2. messages 배열 지원 여부 문의
  3. 멀티턴 대화 로드맵 확인
""")
    
except NameError:
    print("⚠️  일부 테스트를 실행하지 않았습니다.")
    print("   위의 모든 셀을 순서대로 실행해주세요.")

# %% [markdown]
# ---
# # 다음 단계 가이드

# %% 27. 다음 단계 가이드
print("\n" + "="*80)
print("🚀 다음 단계")
print("="*80)
print("""
1️⃣  개발팀과 공유할 내용:
   - 이 테스트 결과 리포트
   - TEST 2 실패 시: Tool 결과 반영 기능 요청
   - messages 배열 형식 지원 여부 확인

2️⃣  POTENS API 문서 재확인:
   - 멀티턴 대화 공식 지원 방식 확인
   - conversation_id나 session_id 파라미터 존재 여부
   - 대화 이력 관리 best practice

3️⃣  교육 과정 조정:
   - TEST 결과에 따라 커리큘럼 수정
   - Pseudo-Agent vs Chain 중심 결정
   - 실습 난이도 조정

4️⃣  추가 테스트 (필요 시):
   - 더 긴 대화 (10턴 이상)
   - 실제 CSV 데이터 로드 테스트
   - 에러 복구 시나리오
""")