
# 샘플 데이터셋 설명서

생성일: 2025-11-13 06:23:56

## 1. sample_basic.csv (기본 실습용)

**목적**: Streamlit UI 및 기본 Agent 실습
**행 수**: 100
**컬럼**: 8개

| 컬럼명 | 타입 | 설명 | 결측치 |
|--------|------|------|--------|
| id | int | 고유 ID | 0 |
| name | str | 이름 | 0 |
| age | int | 나이 (20-65세) | 0 |
| gender | str | 성별 (M/F) | 0 |
| city | str | 도시 | 0 |
| salary | int | 연봉 | 5 |
| experience_years | int | 경력 연수 | 0 |
| score | float | 평가 점수 | 3 |

**실습 가능 분석**:
- 기본 통계 (평균, 최대, 최소)
- 그룹별 집계 (도시별, 성별)
- 결측치 처리 연습
- 간단한 시각화

---

## 2. sample_ecommerce.csv (전자상거래 분석용)

**목적**: EDA Agent 실습, 인사이트 발굴
**행 수**: 1000
**컬럼**: 9개

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| customer_id | int | 고객 ID |
| age | int | 나이 (20-70세) |
| gender | str | 성별 (M/F) |
| region | str | 지역 (서울, 경기, 부산, 대구, 기타) |
| purchase_count | int | 구매 횟수 |
| total_amount | int | 총 구매액 |
| avg_rating | float | 평균 평점 (1-5) |
| is_premium | int | 프리미엄 회원 여부 (0/1) |
| signup_date | date | 가입일 |

**숨겨진 인사이트** (Agent가 발견해야 함):
1. 💎 프리미엄 고객의 구매액이 일반 고객의 2배
2. 🏙️ 서울 고객의 평점이 타 지역보다 높음
3. 👔 40대의 구매 횟수가 가장 많음
4. 👩 여성 고객의 평점이 남성보다 약간 높음

**실습 가능 분석**:
- 고객 세그먼테이션
- RFM 분석
- 상관관계 분석
- 지역/연령대별 구매 패턴

---

## 3. sample_hr.csv (인사 데이터 분석용)

**목적**: HR 분석, 퇴사 예측
**행 수**: 500
**컬럼**: 12개

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| employee_id | int | 직원 ID |
| name | str | 이름 |
| age | int | 나이 (25-60세) |
| gender | str | 성별 (M/F) |
| department | str | 부서 |
| position | str | 직급 |
| years_at_company | int | 근속 연수 |
| salary | int | 연봉 |
| performance_score | float | 성과 점수 |
| overtime_hours | int | 월 평균 야근 시간 |
| satisfaction_score | float | 만족도 (1-5) |
| has_resigned | int | 퇴사 여부 (0/1) |

**숨겨진 인사이트** (Agent가 발견해야 함):
1. 💻 개발 부서의 연봉이 20% 높음
2. 📊 직급별 연봉 차이 명확 (사원 기준 부장 2.5배)
3. 😰 야근이 많으면 만족도 낮음 (부정적 상관관계)
4. 🚪 만족도가 낮으면 퇴사율 높음

**실습 가능 분석**:
- 부서/직급별 연봉 분석
- 퇴사 원인 분석
- 만족도 영향 요인 분석
- 성과-보상 상관관계

---

## 활용 가이드

### lab2 (Pandas Pseudo-Agent)
→ `sample_basic.csv` 사용 권장
- 간단한 구조로 Agent 작동 이해에 집중

### lab3-2 (Streamlit + Agent)
→ `sample_basic.csv` 또는 `sample_ecommerce.csv`
- UI 테스트는 basic
- 실전 분석은 ecommerce

### lab4 (EDA Agent)
→ `sample_ecommerce.csv` 또는 `sample_hr.csv` 필수
- 인사이트 발굴이 목적이므로 패턴이 있는 데이터 필요

### 추가 실습
→ 자유롭게 선택
- 학습자가 관심 있는 도메인 선택

---

## 참고 사항

1. **한글 인코딩**: utf-8-sig로 저장되어 Excel에서도 정상 표시
2. **결측치**: basic 데이터에만 일부 포함 (결측치 처리 실습용)
3. **재현성**: random seed=42 고정 (같은 데이터 생성 가능)
4. **패턴**: 각 데이터셋에 의도적 패턴 포함 (교육 효과)

