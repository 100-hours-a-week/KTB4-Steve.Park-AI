# Pandas 미니퀘스트 모음 (기본 + 데이터 변환)
import pandas as pd
import numpy as np
from utils.utils import printanswer

# ============================================================
# Pandas Quest 1 - Series
# ============================================================
print("\n===== Pandas Quest 1 - Series =====")

## 1
array = [5,10,15,20]
series = pd.Series(array)

printanswer(1, series)

## 2
dict = {'a': 100, 'b': 200, 'c': 300}
series = pd.Series(dict)

printanswer(2, series['b'])

## 3
series = pd.Series([1,2,None,4,None,6])
series = series.fillna(0).astype(int)

printanswer(3, series.values)

# ============================================================
# Pandas Quest 2 - DataFrame
# ============================================================
print("\n===== Pandas Quest 2 - DataFrame =====")

## 1
data = {'이름': ['홍길동','김철수','박영희'],
        '나이': [25, 30, 28],
        '성별': ['남', '남', '여']}
df = pd.DataFrame(data)
printanswer(1, df['이름'].values)

## 2
data = {'이름': ['홍길동','김철수','박영희'],
        '나이': [25, 30, 28],
        '성별': ['남', '남', '여']}
df = pd.DataFrame(data)

df2 = df.sort_values(by='나이')

printanswer(2, df2)

## 3
data = {'이름': ['홍길동','김철수','박영희', '이순신'],
        '국어': [85,90,88,92],
        '영어': [78,85,89,87],
        '수학': [92,88,84,90]}
df = pd.DataFrame(data)
df['총점'] = df['국어'] + df['영어'] + df['수학']

df2 = df[df['총점'] >= 250]
printanswer(3, df2)

# ============================================================
# Data Mutation Quest 1 - Filtering (필터링)
# ============================================================
print("\n===== Data Mutation Quest 1 - Filtering (필터링) =====")

## 1
data = {'이름': ['홍길동', '김철수', '박영희', '이순신', '강감찬'],
        '나이': [25, 30, 35, 40, 45],
        '도시': ['서울', '부산', '서울', '대구', '부산']}

df = pd.DataFrame(data)
df = df[df['나이'] >= 30]

printanswer(1, df)

## 2
data = {'이름': ['홍길동', '김철수', '박영희', '이순신', '강감찬'],
        '나이': [25, 30, 35, 40, 45],
        '도시': ['서울', '부산', '서울', '대구', '부산'],
        '점수': [85, 90, 75, 95, 80]}

df = pd.DataFrame(data)
df = df[(df['도시'] =='서울') | (df['점수'] >= 80)]

printanswer(2, df)

## 3
data = {'이름': ['홍길동', '김철수', '박영희', '이순신', '강감찬'],
        '나이': [25, 30, 35, 40, 45],
        '도시': ['서울', '부산', '서울', '대구', '부산'],
        '점수': [85, 90, 75, 95, 80]}

df = pd.DataFrame(data)
df = df.query("나이 >= 35 and 점수 > 80")

printanswer(3, df)

# ============================================================
# Data Mutation Quest 2 - Grouping (그룹화)
# ============================================================
print("\n===== Data Mutation Quest 2 - Grouping (그룹화) =====")

## 1
data = {
    '이름': ['홍길동', '김철수', '박영희', '이순신'],
    '부서': ['영업', '영업', '인사', '인사'],
    '급여': [5000, 5500, 4800, 5100]
}

df = pd.DataFrame(data)
df = df.groupby('부서')['급여'].sum().reset_index()

printanswer(1, df)

## 2
data = {
    '이름': ['홍길동', '김철수', '박영희', '이순신', '강감찬', '신사임당'],
    '부서': ['영업', '영업', '인사', '인사', 'IT', 'IT'],
    '급여': [5000, 5500, 4800, 5100, 6000, 6200]
}

df = pd.DataFrame(data)
df = df.groupby('부서')['급여'].agg(['sum', 'mean']).reset_index()

printanswer(2, df)

## 3
data = {
    '이름': ['홍길동', '김철수', '박영희', '이순신', '강감찬', '신사임당'],
    '부서': ['영업', '영업', '인사', '인사', 'IT', 'IT'],
    '급여': [5000, 5500, 4800, 5100, 6000, 6200]
}

df = pd.DataFrame(data)
df = df.groupby('부서').filter(lambda x: x['급여'].mean() >= 5000)

printanswer(3, df)

# ============================================================
# Data Mutation Quest 3 - Merge (병합)
# ============================================================
print("\n===== Data Mutation Quest 3 - Merge (병합) =====")

## 1
df1 = pd.DataFrame({'고객ID': [1, 2, 3], '이름': ['홍길동', '김철수', '이영희']})
df2 = pd.DataFrame({'고객ID': [2, 3, 4], '구매액': [10000, 20000, 30000]})

df = pd.merge(df1, df2, on='고객ID', how='inner')

printanswer(1, df)

## 2
df1 = pd.DataFrame({'고객ID': [1, 2, 3], '이름': ['홍길동', '김철수', '이영희']})
df2 = pd.DataFrame({'고객ID': [2, 3, 4], '구매액': [15000, 25000, 35000]})

df = pd.merge(df1, df2, on='고객ID', how='left')

printanswer(2, df)

## 3
df1 = pd.DataFrame({
    '고객ID': [1, 2, 3],
    '도시': ['서울', '부산', '대전'],
    '구매액': [10000, 20000, 30000]
})

df2 = pd.DataFrame({
    '고객ID': [1, 2, 3],
    '도시': ['서울', '부산', '광주'],
    '구매액': [15000, 25000, 35000]
})

df = pd.merge(df1, df2, on=['고객ID', '도시'], how='inner', suffixes=('_하위', '_상위'))

printanswer(3, df)

# ============================================================
# Data Mutation Quest 4 - Missing Data (결측값 처리)
# ============================================================
print("\n===== Data Mutation Quest 4 - Missing Data (결측값 처리) =====")

## 1
data = {'이름': ['홍길동', '김철수', np.nan, '이영희'],
        '나이': [25, np.nan, 30, 28],
        '성별': ['남', '남', '여', np.nan]}

df = pd.DataFrame(data)

printanswer(1, df.isnull().sum())

## 2
data = {'이름': ['홍길동', '김철수', np.nan, '이영희'],
        '나이': [25, np.nan, 30, 28],
        '성별': ['남', '남', '여', np.nan]}

df = pd.DataFrame(data)
df = df.dropna()

printanswer(2, df)

## 3
data = {'이름': ['홍길동', '김철수', np.nan, '이영희'],
        '나이': [25, np.nan, 30, 28],
        '성별': ['남', '남', '여', np.nan]}

df = pd.DataFrame(data)

df['나이'] = df['나이'].fillna(df['나이'].mean())

printanswer(3, df)

# ============================================================
# Data Mutation Quest 5 - Pivot (피벗)
# ============================================================
print("\n===== Data Mutation Quest 5 - Pivot (피벗) =====")

## 1
data = {
    '날짜': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
    '제품': ['A', 'B', 'A', 'B'],
    '판매량': [100, 200, 150, 250]
}

df = pd.DataFrame(data)
df = df.pivot(index='날짜', columns='제품', values='판매량')

printanswer(1, df)

## 2
data = {
    '카테고리': ['전자', '가전', '전자', '가전'],
    '제품': ['A', 'B', 'A', 'B'],
    '판매량': [100, 200, 150, 250]
}

df = pd.DataFrame(data)

df = df.pivot_table(index='카테고리', columns='제품', values='판매량', aggfunc=['sum'])

printanswer(2, df)

## 3
data = {
    '날짜': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
    '제품': ['A', 'B', 'A', 'B'],
    '판매량': [100, 200, 150, 250],
    '이익': [20, 50, 30, 60]
}

df = pd.DataFrame(data)

df = df.pivot(index='날짜', columns='제품', values=['판매량', '이익'])

printanswer(3, df)

# ============================================================
# Data Mutation Quest 6 - Duplicates Removal (중복 제거)
# ============================================================
print("\n===== Data Mutation Quest 6 - Duplicates Removal (중복 제거) =====")

## 1
data = {
    '이름': ['김철수', '이영희', '김철수', '박민수'],
    '나이': [25, 30, 25, 40],
    '성별': ['남', '여', '남', '남']
}

df = pd.DataFrame(data)
df = df.drop_duplicates()

printanswer(1, df)

## 2
data = {
    '제품': ['노트북', '태블릿', '노트북', '스마트폰'],
    '가격': [1500000, 800000, 1500000, 1000000],
    '카테고리': ['전자기기', '전자기기', '전자기기', '전자기기']
}

df = pd.DataFrame(data)

df = df.drop_duplicates(subset='제품')
df['중복여부'] = df.duplicated()

printanswer(2, df)

## 3
data = {
    '학생': ['김민수', '박지현', '김민수', '이정훈'],
    '성적': [90, 85, 90, 88],
    '학교': ['A고', 'B고', 'A고', 'C고']
}

df = pd.DataFrame(data)

df.drop_duplicates(inplace=True)
df.to_csv('data/unique_data.csv', index=False)

printanswer(3, df)

df_loaded = pd.read_csv('data/unique_data.csv')

printanswer(3, df_loaded)

# ============================================================
# Data Mutation Quest 7 - String Operations (문자열 처리)
# ============================================================
print("\n===== Data Mutation Quest 7 - String Operations (문자열 처리) =====")

## 1
data = pd.Series(["HELLO", "WORLD", "PYTHON", "PANDAS"])

df = pd.DataFrame(data)
df = df[0].str.lower()

printanswer(1, df)

## 2
df = pd.DataFrame({"이름": [" John Doe ", "Alice ", " Bob", "Charlie Doe "]})

df['이름'] =  df['이름'].str.strip()
df['이름 포함'] = df["이름"].str.contains('Doe')

printanswer(2, df)

## 3
df = pd.DataFrame({"설명": ["빅데이터 분석", "데이터 과학", "머신 러닝", "딥 러닝"]})

df['설명_분리'] = df['설명'].str.split(' ')
print(df)
df['약어'] = df['설명_분리'].str[0].str[0] + df['설명_분리'].str[1].str[0]

printanswer(3, df)
