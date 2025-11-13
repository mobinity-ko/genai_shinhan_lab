"""
핸즈온 랩 4: 자율적 EDA (탐색적 데이터 분석) Agent (완전 수정 버전)
소요 시간: 30분
난이도: ⭐⭐⭐⭐

학습 목표:
1. 포괄적 목표를 자율적으로 달성하는 Agent 구축
2. EDA 프로세스의 자동화
3. 비즈니스 인사이트 자동 발굴

🔧 개선 사항:
- 코드 파싱 강화 (모든 형식 지원)
- 표현식 평가 (eval) 추가
- print 출력 캡처
- 에러 처리 개선
"""
# %%
import pandas as pd
import numpy as np
import re
import sys
from io import StringIO
from typing import Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from potens_wrapper import PotensChatModel

# %% [markdown]
# # Part 1: EDA Agent 시스템 프롬프트

# %% 1-1. EDA Agent 전용 시스템 프롬프트

EDA_SYSTEM_PROMPT = """
당신은 탐색적 데이터 분석(EDA) 전문가입니다.

**목표:** 사용자가 제공한 목표를 달성하기 위해 자율적으로 데이터를 분석하세요.

**중요 규칙:**
1. pandas(pd)와 numpy(np)는 이미 import되어 있습니다 - 다시 import하지 마세요!
2. DataFrame 변수명은 'df'를 사용하세요
3. 코드를 제안한 후에는 반드시 "Observation: [결과]"를 기다리세요!
4. 절대 코드 실행 결과를 예상하거나 추측하지 마세요!
5. Observation을 받은 후에만 다음 Thought와 Action을 제시하세요!

**분석 프로세스:**
1. 데이터 기본 구조 파악 (shape, dtypes, describe)
2. 결측치 및 이상치 확인
3. 주요 변수 간 관계 분석 (correlation, groupby)
4. 패턴 및 이상 현상 탐지
5. 비즈니스 인사이트 도출

**작업 형식:**
Thought: (현재 단계에서 무엇을 해야 할지)
Action: python_repl
Action Input:
# pandas와 numpy는 이미 import되어 있음! 바로 사용하세요.
(실행할 Python 코드)

**최종 답변 형식 (충분한 분석 후에만):**
Final Answer: 
## 인사이트 1: [제목]
- 발견: [실제 데이터에서 확인한 구체적 수치]
- 의미: [비즈니스적 해석]
- 제안: [실행 가능한 액션]

## 인사이트 2: ...

## 인사이트 3: ...

**필수 규칙:**
- 최소 5번 이상 코드를 실행하고 결과를 확인한 후 Final Answer 제시
- 모든 인사이트는 실제 Observation에서 얻은 수치 기반
- 추측이나 가정 금지 - 오직 데이터가 보여주는 것만 보고
- 각 분석은 이전 Observation을 기반으로 진행
"""

print("✅ EDA Agent 시스템 프롬프트 정의 완료")

# %% [markdown]
# ---
# # Part 2: EDA Agent 클래스 구현 (개선 버전)

# %% 2-1. EDA Agent 클래스

class EDAAgent:
    """
    자율적으로 EDA를 수행하는 Agent (완전 개선 버전)
    """
    
    def __init__(self, chat_model: PotensChatModel, df: pd.DataFrame):
        self.chat_model = chat_model
        self.df = df
        self.messages = [SystemMessage(content=EDA_SYSTEM_PROMPT)]
        self.execution_history = []
    
    def run(self, goal: str, max_iterations: int = 10):
        """
        목표를 달성할 때까지 자율적으로 분석
        
        Args:
            goal: 분석 목표
            max_iterations: 최대 반복 횟수
        
        Returns:
            최종 인사이트
        """
        print("="*80)
        print("🤖 EDA Agent 시작")
        print("="*80)
        print(f"📊 데이터: {self.df.shape[0]}행 x {self.df.shape[1]}컬럼")
        print(f"🎯 목표: {goal}")
        print(f"🔄 최대 반복: {max_iterations}회")
        print("="*80)
        
        # 초기 메시지: 목표 + 데이터 정보
        data_info = self._get_data_info()
        initial_message = f"""
**목표:** {goal}

**데이터 정보:**
{data_info}

위 목표를 달성하기 위해 단계별로 분석을 시작하세요.
"""
        self.messages.append(HumanMessage(content=initial_message))
        
        # 반복 실행
        for i in range(max_iterations):
            print(f"\n{'─'*80}")
            print(f"🔄 반복 {i+1}/{max_iterations}")
            print(f"{'─'*80}")
            
            # Agent에게 다음 행동 요청
            response = None
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    print(f"\n⏳ Agent에게 요청 중... (시도 {attempt + 1}/{max_retries})")
                    response = self.chat_model.invoke(self.messages)
                    break  # 성공하면 루프 탈출
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"\n⚠️ API 에러 발생: {error_msg[:100]}...")
                    
                    if attempt < max_retries - 1:
                        import time
                        wait_time = (attempt + 1) * 2  # 2초, 4초, 6초
                        print(f"   {wait_time}초 후 재시도...")
                        time.sleep(wait_time)
                    else:
                        print(f"\n❌ {max_retries}번 시도 후 실패")
                        return f"API 에러로 인한 조기 종료. 현재까지 {len(self.execution_history)}개 코드 실행 완료."
            
            if not response:
                continue
                
            print(f"\n🤖 Agent 응답:\n{response.content[:500]}...")
            
            self.messages.append(response)
            
            # Final Answer 확인
            if "Final Answer:" in response.content:
                print("\n" + "="*80)
                print("✅ EDA 완료!")
                print("="*80)
                return self._extract_final_answer(response.content)
            
            # Action Input 추출 및 실행
            code = self._extract_code(response.content)
            if code:
                print(f"\n📝 실행할 코드:\n{code}")
                
                # 코드 실행
                result = self._safe_exec(code)
                print(f"\n📊 실행 결과:\n{result}")
                
                # 실행 이력 저장
                self.execution_history.append({
                    "iteration": i + 1,
                    "code": code,
                    "result": result
                })
                
                # Observation 추가
                self.messages.append(
                    HumanMessage(content=f"Observation: {result}")
                )
            else:
                print("\n⚠️ Action Input을 찾을 수 없습니다.")
                break
        
        print("\n⚠️ 최대 반복 횟수 도달")
        return "최대 반복 횟수 초과. Final Answer를 받지 못했습니다."
    
    def _get_data_info(self) -> str:
        """데이터 기본 정보 생성 (간결 버전)"""
        info_lines = [
            f"- Shape: {self.df.shape[0]}행 x {self.df.shape[1]}컬럼",
            f"- 컬럼: {', '.join(self.df.columns.tolist())}",
        ]
        
        # 타입은 요약만
        type_summary = {}
        for dtype in self.df.dtypes.unique():
            count = (self.df.dtypes == dtype).sum()
            type_summary[str(dtype)] = count
        info_lines.append(f"- 타입 요약: {type_summary}")
        
        # 결측치는 있는 것만
        missing = self.df.isnull().sum()
        missing_cols = missing[missing > 0]
        if len(missing_cols) > 0:
            info_lines.append(f"- 결측치: {missing_cols.to_dict()}")
        else:
            info_lines.append("- 결측치: 없음")
        
        return "\n".join(info_lines)
    
    def _extract_code(self, response_text: str) -> str:
        """
        Agent 응답에서 코드 추출 (완전 개선 버전)
        
        지원하는 형식:
        1. ```python ... ```
        2. ``` ... ```
        3. Action Input: code
        4. Action Input:\ncode
        """
        # 패턴 1: 코드 블록 먼저 시도
        pattern = r"```(?:python)?\s*(.*?)\s*```"
        matches = re.findall(pattern, response_text, re.DOTALL)
        if matches:
            code = matches[0].strip()
            # 주석 제거 (선택사항)
            code_lines = [line for line in code.split("\n") 
                         if line.strip() and not line.strip().startswith("#")]
            if code_lines:
                return "\n".join(code_lines)
        
        # 패턴 2: Action Input: 이후
        if "Action Input:" in response_text:
            after_action_input = response_text.split("Action Input:")[1]
            lines = after_action_input.split("\n")
            
            code_lines = []
            in_code_block = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # 코드 블록 마커
                if stripped.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                
                # 종료 조건
                if not in_code_block:
                    if stripped.startswith("Observation") or \
                       stripped.startswith("Thought") or \
                       stripped.startswith("Final Answer") or \
                       stripped.startswith("Action:"):
                        break
                    
                    if not stripped and code_lines:
                        break
                
                # 첫 줄 처리
                if i == 0 and stripped and not stripped.startswith("```"):
                    code_lines.append(line)
                elif stripped or in_code_block:
                    code_lines.append(line)
            
            if code_lines:
                return "\n".join(code_lines).strip()
        
        return None
    
    def _safe_exec(self, code: str) -> Any:
        """
        코드를 안전하게 실행 (완전 개선 버전)
        
        개선사항:
        1. 표현식 평가 (eval)
        2. print 출력 캡처
        3. 에러 처리 강화
        4. 불필요한 import 제거
        5. 중복 출력 방지
        """
        try:
            # 불필요한 import 제거 (이미 globals에 있음)
            code = code.replace("import pandas as pd", "").strip()
            code = code.replace("import numpy as np", "").strip()
            
            # 빈 코드면 건너뛰기
            if not code:
                return "⚠️ 실행할 코드가 없습니다 (import만 있었음)"
            
            # stdout 캡처
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            safe_globals = {
                "pd": pd,
                "np": np,
                "df": self.df,
                "__builtins__": {
                    "len": len, "sum": sum, "max": max, "min": min,
                    "round": round, "print": print, "str": str,
                    "int": int, "float": float, "list": list, "dict": dict,
                    "abs": abs, "any": any, "all": all,
                    "range": range, "enumerate": enumerate, "sorted": sorted,
                    "zip": zip, "map": map, "filter": filter,
                    "set": set, "tuple": tuple, "bool": bool,
                }
            }
            
            local_vars = {}
            
            # 코드 실행
            exec(code, safe_globals, local_vars)
            
            # stdout 복원
            sys.stdout = old_stdout
            printed_output = captured_output.getvalue()
            
            # 결과 수집
            results = []
            
            # 1. print 출력 (최우선)
            if printed_output.strip():
                # 너무 긴 출력은 잘라내기 (타임아웃 방지)
                output = printed_output.strip()
                if len(output) > 2000:
                    output = output[:1000] + "\n... (중략) ...\n" + output[-1000:]
                results.append(output)
                
                # print가 있으면 변수 결과는 생략 (중복 방지)
                if len(output) > 100:
                    return output
            
            # 2. 변수 결과 (print가 없거나 짧을 때만)
            if local_vars:
                if "result" in local_vars:
                    result_value = local_vars["result"]
                else:
                    result_value = local_vars[list(local_vars.keys())[-1]]
                
                formatted = self._format_result(result_value)
                results.append(formatted)
            
            # 3. 표현식 평가 (변수도 없고 출력도 없으면)
            elif not results:
                try:
                    result_value = eval(code, safe_globals, {})
                    results.append(self._format_result(result_value))
                except:
                    pass
            
            # 결과 반환
            if results:
                final_result = "\n\n".join(results)
                # 최종 결과도 길이 제한 (타임아웃 방지)
                if len(final_result) > 2000:
                    final_result = final_result[:1000] + "\n\n... (결과가 너무 길어 중략) ...\n\n" + final_result[-1000:]
                return final_result
            else:
                return "✅ 실행 완료"
                
        except Exception as e:
            sys.stdout = old_stdout
            error_msg = str(e)
            # 에러 메시지도 길이 제한
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "..."
            return f"❌ 에러: {error_msg}"
    
    def _format_result(self, result_value):
        """결과 포맷팅 (간결 버전)"""
        if isinstance(result_value, pd.DataFrame):
            # 간결한 요약만
            summary = f"DataFrame({result_value.shape[0]}행 x {result_value.shape[1]}컬럼)"
            # 작은 DataFrame만 내용 표시
            if result_value.shape[0] <= 5 and result_value.shape[1] <= 5:
                summary += f"\n{result_value.to_string()}"
            return summary
        elif isinstance(result_value, pd.Series):
            summary = f"Series(길이 {len(result_value)})"
            if len(result_value) <= 10:
                summary += f"\n{result_value.to_string()}"
            return summary
        else:
            result_str = str(result_value)
            # 긴 결과는 잘라내기
            if len(result_str) > 1000:
                result_str = result_str[:500] + "\n...(중략)..." + result_str[-500:]
            return result_str
    
    def _extract_final_answer(self, response_text: str) -> str:
        """Final Answer 추출"""
        if "Final Answer:" in response_text:
            return response_text.split("Final Answer:")[1].strip()
        return response_text
    
    def show_history(self):
        """실행 이력 표시"""
        print("\n" + "="*80)
        print("📜 실행 이력")
        print("="*80)
        for item in self.execution_history:
            print(f"\n[{item['iteration']}회차]")
            print(f"코드: {item['code'][:100]}...")
            print(f"결과: {str(item['result'])[:100]}...")

# %% [markdown]
# ---
# # Part 3: 샘플 데이터 생성 및 테스트

# %% 3-1. 샘플 데이터 생성

# 전자상거래 매출 데이터 생성
np.random.seed(42)

n_customers = 100

sample_df = pd.DataFrame({
    'customer_id': range(1, n_customers + 1),
    'age': np.random.randint(20, 70, n_customers),
    'gender': np.random.choice(['M', 'F'], n_customers),
    'region': np.random.choice(['서울', '경기', '부산', '기타'], n_customers),
    'purchase_count': np.random.poisson(5, n_customers),
    'total_amount': np.random.exponential(300000, n_customers),
    'avg_rating': np.random.uniform(1, 5, n_customers),
    'is_premium': np.random.choice([0, 1], n_customers, p=[0.7, 0.3])
})

# 일부러 패턴 추가 (인사이트 발굴용)
sample_df.loc[sample_df['is_premium'] == 1, 'total_amount'] *= 2
sample_df.loc[sample_df['region'] == '서울', 'avg_rating'] += 0.5
sample_df['avg_rating'] = sample_df['avg_rating'].clip(1, 5)
sample_df.loc[sample_df['age'].between(40, 49), 'purchase_count'] += 2

print("✅ 샘플 데이터 생성 완료")
print(sample_df.head())

# %% 3-2. EDA Agent 실행

# Agent 초기화
chat_model = PotensChatModel()
eda_agent = EDAAgent(chat_model, sample_df)

# 실행
insights = eda_agent.run(
    goal="매출 증대를 위한 실행 가능한 비즈니스 인사이트 3개를 찾아주세요",
    max_iterations=8
)

# 최종 결과 출력
print("\n" + "="*80)
print("📊 최종 인사이트")
print("="*80)
print(insights)

# %% 3-3. 실행 이력 확인

eda_agent.show_history()

# %% [markdown]
# ---
# # 🎉 실습 완료!
# 
# ## 배운 내용:
# 1. ✅ 자율적 EDA Agent 구현
# 2. ✅ 강화된 코드 파싱 (모든 형식 지원)
# 3. ✅ 표현식 평가 및 print 캡처
# 4. ✅ 비즈니스 인사이트 도출
# 
# ## 개선 사항:
# - 코드 블록(```) 우선 파싱
# - 표현식 자동 평가
# - print 출력 캡처
# - 에러 처리 강화
# 
# ## 💡 실무 적용:
# - 탐색 시간 50% 단축
# - DA는 검증 및 심화에 집중
# - 반복 작업 자동화