#%%
# === 1. 기본 설정 (ReAct가 성공한 01번 코드와 동일) ===
import os
import pandas as pd
from dotenv import load_dotenv
from custom_llm import PotensChatLLM # ReAct가 성공한 커스텀 LLM
from langchain_community.agent_toolkits import create_pandas_dataframe_agent

load_dotenv()
llm = PotensChatLLM()
df = pd.read_csv("data/sample_transactions.csv")

# (중요) ReAct가 성공한 'ZERO_SHOT_REACT_DESCRIPTION' 사용
agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    agent_type="zero-shot-react-description",
    allow_dangerous_code=True
)
print("✅ Agent (ReAct 기반) 생성 완료. 멀티턴 테스트를 시작합니다.")

#%%
# === 2. 멀티턴 테스트 (Turn 1) ===
# 첫 번째 질문: 데이터를 조회합니다.
question1 = "총 매출(TotalPrice)이 가장 높은 상위 3개의 거래를 보여줘."

print(f"\n--- [Turn 1] 질문: {question1} ---")
response1 = agent.invoke(question1)
print("\n[Turn 1] 답변:")
print(response1['output'])

#%%
# === 3. 멀티턴 테스트 (Turn 2) ===
# (중요) 첫 번째 질문의 '결과'를 참조하는 두 번째 질문을 합니다.
# "그 거래들"이 'response1'의 결과를 의미하는지 Agent가 알아야 합니다.
question2 = "방금 본 그 3개 거래의 'Product'만 알려줘."

print(f"\n--- [Turn 2] 질문: {question2} ---")
response2 = agent.invoke(question2)
print("\n[Turn 2] 답변:")
print(response2['output'])