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
from dotenv import load_dotenv
from openai import OpenAI  # 또는 Anthropic, Google Gemini
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

print("라이브러리 로드 완료!")

# %% [markdown]
# ---
# ### 🚨 Section 1: (The Bad Way) API Key 하드코딩
# 
# 아래와 같이 코드에 API Key를 직접 넣는 것은 **절대** 안 됩니다.
# Git에 커밋하는 순간, API Key가 전 세계에 유출될 수 있습니다.

# %%
# (주의) 이 코드는 예시일 뿐, 절대 실제 키를 넣고 실행하지 마세요!
#
# BAD_CLIENT = OpenAI(
#     api_key="sk-xxxx....(절대 이렇게 쓰지 마세요!)...xxxx"
# )
# print("절대 실행되어서는 안 되는 셀입니다.")

# %% [markdown]
# ---
# ### ✅ Section 2: (The Good Way) .env 파일을 통한 API Key 관리
# 
# `python-dotenv` 라이브러리를 사용해 Key를 환경 변수로 로드합니다.
# 
# **[실습 가이드]**
# 1. 이 `.py` 파일과 **같은 폴더**에 `.env` 라는 이름의 파일을 만듭니다.
# 2. `.env` 파일 안에 강사님이 공유한 API Key를 다음과 같이 입력하고 저장합니다.
#    (Gemini 예시)
#    `GOOGLE_API_KEY=AIzaxxxxx.....xxxxx`

# %%
# === 2. .env 파일 로드 ===

# load_dotenv()가 .env 파일을 찾아 환경 변수로 로드합니다.
# [YOUR_CODE_HERE]
# (힌트) load_dotenv() 함수를 호출하세요.
load_dotenv()

# os.getenv()를 사용해 환경 변수로 로드된 Key를 가져옵니다.
# [YOUR_CODE_HERE]
# (힌트) 변수 API_KEY에 os.getenv("YOUR_ENV_KEY_NAME")을 할당하세요.
# (예: "GOOGLE_API_KEY", "OPENAI_API_KEY")
API_KEY = os.getenv("GOOGLE_API_KEY") # 또는 OPENAI_API_KEY

if not API_KEY:
    print("🚨 [에러] .env 파일에서 API Key를 찾을 수 없습니다.")
    print("    1. .env 파일을 생성했는지 확인하세요.")
    print("    2. Key 이름(예: GOOGLE_API_KEY)이 올바른지 확인하세요.")
else:
    print("✅ [성공] .env 파일에서 API Key를 성공적으로 로드했습니다.")

# %%
# === 3. LLM API 클라이언트 초기화 ===
# (아래는 OpenAI/Google 예시이며, 사용할 API에 맞게 수정합니다)

# [OpenAI 사용 시]
# client = OpenAI(api_key=API_KEY)

# [Google Gemini 사용 시]
import google.generativeai as genai
genai.configure(api_key=API_KEY)

print("사용 가능한 모델:")
# 'generateContent' 메서드를 지원하는 모델 목록을 가져옵니다.
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

# %% 
model = genai.GenerativeModel('models/gemini-2.5-flash') # 사용하고자 하는 모델명 입력
print("✅ Gemini 클라이언트 초기화 완료.")

# %% [markdown]
# ### [실습] My First LLM API Call
# 
# 위에서 초기화한 `model` (또는 `client`)을 사용해 API 호출을 테스트합니다.

# %%
# === 4. API 호출 테스트 ===

try:
    # [Gemini 사용 시]
    # [YOUR_CODE_HERE]
    # (힌트) model.generate_content("...") 를 호출합니다.
    response = model.generate_content("신한카드가 GenAI 교육을 하는 이유에 대해 한 문장으로 요약해줘.")
    print(f"{response.text}")
    
    # [OpenAI 사용 시]
    # response = client.chat.completions.create(
    #     model="gpt-4o", # 또는 gpt-5
    #     messages=[{"role": "user", "content": "신한카드가 GenAI 교육을 하는 이유에 대해 한 문장으로 요약해줘."}]
    # )
    # print(f"API 응답: {response.choices[0].message.content}")

    print("\n✅ [성공] API가 성공적으로 호출되었습니다.")

except Exception as e:
    print(f"🚨 [에러] API 호출에 실패했습니다: {e}")
    print("    1. API Key가 올바른지 확인하세요.")
    print("    2. 인터넷 연결 및 API Quota를 확인하세요.")

# %% [markdown]
# ---
# ### 🔒 Section 3: (The Secure Way) PII 마스킹 (Presidio)
#. 
# 드디어 Day 1의 핵심입니다.
# 고객 VOC 데이터를 API로 요약하고 싶지만, **민감정보(PII)**가 포함되어 있습니다.
# `presidio`를 사용해 PII를 **탐지(Analyze)**하고 **마스킹(Anonymize)**한 후,
# '안전한' 데이터만 LLM API로 전송합니다.

# %%
# === 5. Presidio 엔진 초기화 ===
# (한국어 지원을 위해 ko-medical 모델을 활용하거나, 기본 설정을 사용합니다)
# 여기서는 기본 'en' 설정을 사용하되, 신용카드/전화번호 등은 인식합니다.

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

print("✅ Presidio 엔진 초기화 완료.")

# === 6. 실습 데이터 로드 ===
# (사전 제공된 'sample_customer_query.txt' 파일)
try:
    with open('sample_customer_query.txt', 'r', encoding='utf-8') as f:
        pii_text = f.read()
    print("--- [원본 데이터] ---")
    print(pii_text)
    print("--------------------")
except FileNotFoundError:
    print("🚨 [에러] 'sample_customer_query.txt' 파일을 찾을 수 없습니다.")
    pii_text = ""

# %%
# === 7. PII 탐지 (Analyze) ===
# [YOUR_CODE_HERE]
# (힌트) analyzer.analyze(...)를 사용해 pii_text를 분석합니다.
if pii_text:
    analyzer_results = analyzer.analyze(
        text=pii_text,
        language='en' # (아쉽게도 Presidio는 한국어 공식 지원이 약합니다. 
                      # 하지만 신용카드, 이메일, 전화번호 등 패턴 기반은 인식합니다)
        # (Tip) 한국어 PII(주민번호 등)를 위해 정규식(Regex) 기반 'Recognizer'를 추가할 수 있습니다.
    )

    print(f"✅ 총 {len(analyzer_results)}개의 PII가 탐지되었습니다.")
    for res in analyzer_results:
        print(f"  - {res.entity_type}: {pii_text[res.start:res.end]}")

# %%
# === 8. PII 마스킹 (Anonymize) ===
# 탐지된 PII를 <PHONE_NUMBER>, <CREDIT_CARD_NUMBER> 등으로 대체합니다.

# [YOUR_CODE_HERE]
# (힌트) anonymizer.anonymize(...)를 사용해 마스킹합니다.
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
# === 9. (The Secure Way) 안전한 데이터로 API 호출 ===
# 이제 고객의 민감정보가 제거된 'anonymized_text'를 사용해
# LLM에게 "이 고객의 VOC를 한 문장으로 요약해줘" 라고 요청합니다.

# [YOUR_CODE_HERE]
# (힌트) Section 2에서 사용한 model.generate_content()를 다시 호출하되,
# PII가 마스킹된 'anonymized_text'를 입력값으로 사용합니다.

if 'anonymized_text' in locals():
    try:
        prompt = f"""
        다음은 고객 VOC 내용입니다. 고객의 요청 사항을 한 문장으로 요약해 주세요.

        ---
        {anonymized_text}
        ---
        """
        
        # [Gemini 사용 시]
        response = model.generate_content(prompt)
        print("--- [LLM의 안전한 요약] ---")
        print(response.text)
        
        print("\n✅ [성공] PII를 마스킹하여 안전하게 API를 호출했습니다.")

    except Exception as e:
        print(f"🚨 [에러] 마스킹된 데이터 호출 중 에러 발생: {e}")
else:
    print("🚨 [에러] 마스킹된 텍스트('anonymized_text')가 준비되지 않았습니다.")
# %%
