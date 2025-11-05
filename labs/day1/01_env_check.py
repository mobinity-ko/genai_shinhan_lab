# %% [markdown]
# # Lab 1: 로컬 GenAI 개발 환경 구축
# 
# 이 파일은 6일간의 교육 과정에 필요한 모든 핵심 라이브러리가
# 나의 가상환경(venv)에 올바르게 설치되었는지 확인하는 **'건강 검진'** 파일입니다.
# 
# (오류 발생 시) 강사에게 문의하거나, 오프라인 설치용 USB를 요청하세요.

# %%
# [셀 실행 방법]
# 1. (Shift + Enter)
# 2. 이 셀을 실행했을 때, **오류 없이** 라이브러리 버전과 성공 메시지가 출력되면 환경 구축에 성공한 것입니다.
#
# (참고) __version__ 속성 대신, 설치된 패키지 메타데이터를 직접 읽는
#        'importlib.metadata'를 사용하여 버전을 확인합니다. (가장 안전한 방법)

import sys
import importlib.metadata

print(f"--- 환경 검사 성공 ---")
print(f"Python 버전: {sys.version.split(' ')[0]}\n")

# requirements.txt의 핵심 라이브러리 목록
core_libraries = [
    "pandas",
    "streamlit",
    "torch",
    "langchain",
    "chromadb",
    "ragas",
    "langgraph",
    "presidio-analyzer",
    "numpy",
    "ipywidgets"
]

all_ok = True
for lib in core_libraries:
    try:
        version = importlib.metadata.version(lib)
        print(f"✅ {lib: <20} 버전: {version}")
        
        # (중요) NumPy 2.x 충돌 방지 확인
        if lib == "numpy" and not version.startswith("1."):
            print(f"   🚨 [경고] NumPy 버전이 1.x가 아닙니다. (현재: {version})")
            print(f"   torch, pandas 등과 충돌할 수 있습니다. requirements.txt를 확인하세요.")
            all_ok = False
            
    except importlib.metadata.PackageNotFoundError:
        print(f"❌ [오류] {lib: <20} 라이브러리가 설치되지 않았습니다!")
        all_ok = False

if all_ok:
    print(f"\n[성공] 6일간의 여정을 위한 모든 준비가 완료되었습니다! 🚀")
else:
    print(f"\n[실패] 일부 라이브러리에 문제가 있습니다. 로그를 확인하고 재설치하세요.")


# %% [markdown]
# ### (선택) VS Code + Jupyter 연동 확인

# %%
a = 10
print(f"변수 'a'의 값은: {a}")

# %%
# 이 셀을 실행했을 때, 위 셀의 'a' 값을 이어받아 '11'이 출력되면 연동 성공입니다.
print(f"변수 'a'에 1을 더한 값은: {a + 1}")
# %%
