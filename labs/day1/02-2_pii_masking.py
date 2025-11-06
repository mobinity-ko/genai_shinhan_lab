# %% [markdown]
# ---
# ### 🔒 PII 마스킹 (Presidio)

# 고객 VOC 데이터를 API로 요약하고 싶지만, **민감정보(PII)**가 포함되어 있습니다.
# `presidio`를 사용해 PII를 **탐지(Analyze)**하고 **마스킹(Anonymize)**한 후,
# '안전한' 데이터만 LLM API로 전송합니다.

# %%
# === 1. Presidio 엔진 초기화 ===
# 여기서는 기본 'en' 설정을 사용하되, 신용카드/전화번호 등은 인식합니다.
import os
import requests
from dotenv import load_dotenv
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

print("✅ Presidio 엔진 초기화 완료.")

# %%
# === 2. 실습 데이터 로드 ===
# (사전 제공된 'sample_customer_query.txt' 파일)
try:
    with open('./data/sample_customer_query.txt', 'r', encoding='utf-8') as f:
        pii_text = f.read()
    print("--- [원본 데이터] ---")
    print(pii_text)
    print("--------------------")
except FileNotFoundError:
    print("🚨 [에러] 'sample_customer_query.txt' 파일을 찾을 수 없습니다.")
    pii_text = ""

# %%
# === 3. PII 탐지 (Analyze) ===
# analyzer.analyze(...)를 사용해 pii_text를 분석합니다.
if pii_text:
    analyzer_results = analyzer.analyze(
        text=pii_text,
        language='en' # (아쉽게도 Presidio는 한국어 공식 지원이 약합니다. 
                      # 하지만 신용카드, 이메일, 전화번호 등 패턴 기반은 인식합니다)
        # (Tip) 한국어 PII(전화번호, 주민번호 등)를 위해 정규식(Regex) 기반 'Recognizer'를 추가할 수 있습니다.
    )

    print(f"✅ 총 {len(analyzer_results)}개의 PII가 탐지되었습니다.")
    for res in analyzer_results:
        print(f"  - {res.entity_type}: {pii_text[res.start:res.end]}")

# %%
# === 4. PII 마스킹 (Anonymize) ===
# 탐지된 PII를 <PHONE_NUMBER>, <CREDIT_CARD_NUMBER> 등으로 대체합니다.

# anonymizer.anonymize(...)를 사용해 마스킹합니다.
if analyzer_results:
    anonymized_result = anonymizer.anonymize(
        text=pii_text,
        analyzer_results=analyzer_results
    )
    
    # 마스킹된 텍스트
    anonymized_text = anonymized_result.text

    print("--- [마스킹된 안전한 데이터] ---")
    print(anonymized_text)
    print("------------------------------")

# %%
# === 5. 안전한 데이터로 API 호출 ===
# 이제 고객의 민감정보가 제거된 'anonymized_text'를 사용해
# LLM에게 "이 고객의 VOC를 한 문장으로 요약해줘" 라고 요청합니다.

# Section 2에서 사용한 model.generate_content()를 다시 호출하되,
# PII가 마스킹된 'anonymized_text'를 입력값으로 사용합니다.

API_KEY = os.getenv("POTENS_API_KEY")
API_URL = "https://ai.potens.ai/api/chat"

if 'anonymized_text' in locals() and API_KEY:
    try:
        prompt = f"""
        다음은 고객 VOC 내용입니다. 고객의 요청 사항을 한 문장으로 요약해 주세요.

        ---
        {anonymized_text}
        ---
        """
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "prompt": prompt
        }
        
        print("⏳ 마스킹된 데이터로 LLM API 호출 중...")
        response = requests.post(API_URL, headers=headers, json=body, timeout=30)
        response.raise_for_status()

        api_response = response.json()
        print("--- [LLM의 안전한 요약] ---")
        print(f"{api_response.get('message', '응답 메시지 없음')}")
        
        print("\n✅ [성공] PII를 마스킹하여 안전하게 (자체) API를 호출했습니다.")

    except Exception as e:
        print(f"🚨 [에러] 마스킹된 데이터 호출 중 에러 발생: {e}")
else:
    print("🚨 [에러] 마스킹된 텍스트('anonymized_text')가 준비되지 않았습니다.")
# %%
