# 🚀 신한카드 GenAI 데이터 전문가 양성 과정

본 프로젝트는 6일간의 GenAI 전문가 과정을 위한 공식 실습 저장소입니다.

## 1. 🎯 과정 목표

* GenAI 패러다임을 이해하고 AI와 협업하는 방식을 체득합니다.
* 보안(PII)을 준수하는 현업 적용 가능한 로컬 개발 환경을 구축합니다.
* RAG, Agents, Streamlit 등 최신 오픈소스 스택을 활용한 PoC를 완료합니다.

## 2. 🖥️ 로컬 환경 설정 (필수)

**교육 시작 전 반드시 완료해 주세요!** (현장 WiFi가 매우 느립니다.)

1.  **Git Clone:**
    ```bash
    git clone [본 저장소 URL]
    cd genai_shinhan_lab
    ```

2.  **가상환경(venv) 생성 및 활성화:**
    ```bash
    # (Windows)
    python -m venv venv
    .\venv\Scripts\activate

    # (macOS/Linux)
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **라이브러리 설치 (필수):**
    ```bash
    pip install -r requirements.txt
    ```
    *(설치에 실패할 경우, 강사가 제공하는 오프라인 설치 USB를 이용하세요.)*

4.  **VS Code 실행:**
    ```bash
    code .
    ```
    * VS Code 실행 후, 우측 하단에서 Python 인터프리터가 `(venv)`로 잡혔는지 확인하세요.

5.  **API Key 설정 (Day 1 실습):**
    * `.env.example` 파일을 `.env` 파일로 복사합니다.
    * 강사에게 제공받은 API Key를 `.env` 파일에 입력합니다.

## 3. 🗺️ 프로젝트 구조

* `/data/`: 실습에 필요한 모든 원본/가공 데이터가 있습니다.
* `/labs/`: **우리의 핵심 실습 공간입니다.** `day_01`부터 순서대로 `.py` 파일을 열고, `"# %%"` 셀 단위로 실습을 진행합니다.
* `/src/`: 자주 사용되는 공통 함수가 저장됩니다. (예: `utils.py`)
* `requirements.txt`: 모든 Python 라이브러리 목록입니다.

## 4. 🗓️ 일일 랩 가이드

* **Day 1:** [환경 구축 및 보안 API 호출](./labs/day_01_setup_security/)
* **Day 2:** [DA - LangChain Agent와 Streamlit](./labs/day_02_da_streamlit/)
* **Day 3:** [DE - 로컬 RAG 파이프라인 구축 및 평가](./labs/day_03_de_rag/)
* ... (이하 생략)