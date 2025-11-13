#%%
# === 1. 기본 설정 ===
import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
# .env 파일에서 API 키 로드
# (Colab/Jupyter 등에서는 os.environ["OPENAI_API_KEY"] = "sk-..."로 직접 설정 가능)
load_dotenv()
print("✅ 1. 기본 설정 완료")

#%%
# === 2. LLM (두뇌) 정의 ===
llm = ChatOpenAI(model="gpt-4o", temperature=0)
print("✅ 2. LLM(두뇌) 준비 완료")

#%%
# === 3. 샘플 데이터 (DataFrame) 생성 ===
# 원본 코드의 CSV 로드 대신, 실습을 위해 간단한 샘플 데이터를 직접 생성합니다.
# 날짜, 고객 ID, 주문 ID 등 복잡한 분석이 가능한 데이터로 변경
data = {
    'OrderID': [1001, 1001, 1002, 1003, 1003, 1004, 1005, 1005, 1005, 1006],
    'OrderDate': [
        '2024-01-15', '2024-01-15', '2024-01-17', '2024-01-18', '2024-01-18',
        '2024-02-01', '2024-02-05', '2024-02-05', '2024-02-05', '2024-02-10'
    ],
    'CustomerID': ['C-001', 'C-001', 'C-002', 'C-001', 'C-001', 'C-003', 'C-002', 'C-002', 'C-002', 'C-001'],
    'Product': ['Laptop', 'Mouse', 'T-shirt', 'Keyboard', 'Monitor', 'Shoes', 'Hat', 'Jeans', 'Watch', 'Headphones'],
    'Category': ['Electronics', 'Electronics', 'Apparel', 'Electronics', 'Electronics', 'Apparel', 'Apparel', 'Apparel', 'Accessories', 'Electronics'],
    'Quantity': [1, 1, 2, 1, 1, 1, 3, 1, 1, 1],
    'UnitPrice': [1200, 50, 30, 100, 300, 150, 25, 100, 250, 180]
}
df = pd.DataFrame(data)

# [중요] 'TotalPrice' 컬럼을 'Quantity' * 'UnitPrice'로 생성
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
# [중요] 'OrderDate'를 datetime 객체로 변환 (시간 분석을 위해 필수)
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

print("✅ 3. 고도화된 샘플 데이터 생성 완료")
print(df)

#%%
# === 4. Agent 생성 ===
# verbose=True: Agent의 '사고 과정(ReAct)'을 터미널에 출력합니다.
# allow_dangerous_code=True: Agent가 Pandas 코드를 '실제로' 실행하도록 허용합니다.
agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    agent_type="openai-tools",
    allow_dangerous_code=True,
    # [추가] Agent가 DataFrame의 정보를 더 잘 이해하도록 설명(prefix) 추가
    prefix="""
    당신은 데이터 분석가 역할을 하는 Pandas Agent입니다.
    주어진 DataFrame을 사용하여 질문에 답해야 합니다.
    'OrderDate' 컬럼은 datetime 객체입니다.
    'TotalPrice'는 'Quantity' * 'UnitPrice'의 결과입니다.
    """
)
print("✅ 4. Pandas DataFrame Agent 생성 완료")

#%%
# === 5. Agent 실행 (질문 1: 다단계 계산) ===
print("\n--- [질문 1] Electronics 카테고리의 매출 비중은 전체 매출의 몇 %인가요? ---")
# 이 질문은 다음 단계를 거쳐야 합니다:
# 1. 'Electronics' 매출 합계 계산
# 2. 전체(모든 카테고리) 매출 합계 계산
# 3. (Electronics / 전체) * 100 계산
# Agent가 이 단계를 나누어 생각하는지 관찰해 보세요.
try:
    response1 = agent.invoke("Electronics 카테고리의 매출 비중은 전체 매출의 몇 %인가요?")
    print("\n[최종 답변 1]")
    print(response1['output'])
except Exception as e:
    print(f"[에러 1] {e}")

#%%
# === 6. Agent 실행 ===
print("\n--- [질문 2] 가장 많은 돈을 쓴 고객(CustomerID)은 누구이며, 이 고객이 가장 많이 구매한 제품 카테고리(Category)는 무엇인가요? ---")
# 1. 고객(CustomerID)별로 'TotalPrice' 합계 계산
# 2. 1번 결과에서 합계가 가장 높은 'CustomerID' 찾기 (예: 'C-001')
# 3. 원본 DataFrame을 2번에서 찾은 'CustomerID'로 필터링
# 4. 3번의 필터링된 데이터에서 'Category'별로 구매 건수(또는 수량) 집계
# 5. 4번 결과에서 가장 높은 'Category' 찾기
try:
    response3 = agent.invoke("가장 많은 돈을 쓴 고객(CustomerID)은 누구이며, 이 고객이 가장 많이 구매한 제품 카테고리(Category)는 무엇인가요?")
    print("\n[최종 답변 3]")
    print(response3['output'])
except Exception as e:
    print(f"[에러 3] {e}")

# %%
