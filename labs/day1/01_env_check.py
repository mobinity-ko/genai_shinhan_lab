# %% [markdown]
# # Lab 1: 로컬 GenAI 개발 환경 구축
# 
# 이 파일은 6일간의 교육 과정에 필요한 모든 핵심 라이브러리가
# 나의 가상환경(venv)에 올바르게 설치되었는지 확인하는 **'건강 검진'** 파일입니다.
# 
# (오류 발생 시) 강사에게 문의하거나, 오프라인 설치용 USB를 요청하세요.

# %%
# [셀 실행 방법]
# 1. 이 셀에 마우스 커서를 올리면 좌측 상단에 'Run Cell' 버튼이 보입니다. (혹은 Shift + Enter)
# 2. 이 셀을 실행했을 때, **오류 없이** 라이브러리 버전과 성공 메시지가 출력되면 환경 구축에 성공한 것입니다.

import os
import sys
import pandas as pd
import streamlit as st
import torch
import langchain
import chromadb
import ragas
import langgraph
import presidio_analyzer
import presidio_anonymizer

print(f"--- 환경 검사 성공 ---")
print(f"Python 버전: {sys.version.split(' ')[0]}")
print(f"Pandas 버전: {pd.__version__}")
print(f"Streamlit 버전: {st.__version__}")
print(f"PyTorch 버전: {torch.__version__}")
print(f"LangChain 버전: {langchain.__version__}")
print(f"ChromaDB 버전: {chromadb.__version__}")
print(f"RAGAs 버전: {ragas.__version__}")
print(f"LangGraph 버전: {langgraph.__version__}")
print(f"Presidio (PII) 버전: {presidio_analyzer.__version__}")
print(f"\n[성공] 6일간의 여정을 위한 모든 준비가 완료되었습니다! 🚀")

# %% [markdown]
# ### (선택) VS Code + Jupyter 연동 확인
# 
# 위 셀에서 라이브러리 버전이 잘 출력되었다면,
# 이제 VS Code가 Jupyter 커널(가상환경)을 잘 인식하고 있는지 확인합니다.

# %%
# 이 셀을 실행했을 때, 'a'의 값인 10이 출력되면 정상입니다.
a = 10
print(f"변수 'a'의 값은: {a}")

# %%
# 이 셀을 실행했을 때, 위 셀에서 정의한 'a'의 값을
# 이어서 사용할 수 있다면(11 출력) 연동에 성공한 것입니다.
print(f"변수 'a'에 1을 더한 값은: {a + 1}")