import pandas as pd

def calculate_average_age(data):
    # 버그 1: 'Age'가 아니라 'age' (대소문자)
    # 버그 2: 나이가 숫자가 아닌 문자열 (Type Error)
    total_age = 0
    count = 0
    for person in data:
        total_age += person['Age']
        count += 1
    
    # 버그 3: 0으로 나누기 (ZeroDivisionError)
    return total_age / count

# 테스트 데이터
users = [
    {'name': 'Kim', 'age': '30'},
    {'name': 'Lee', 'age': '45'},
    {'name': 'Park', 'age': '22'}
]

# 실행 시 에러 발생
# print(calculate_average_age(users))

# 빈 리스트를 넣을 경우 에러 발생
# print(calculate_average_age([]))