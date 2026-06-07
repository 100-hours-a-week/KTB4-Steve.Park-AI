# Week 03 - NumPy, Pandas & 데이터 시각화 미니퀘스트

> KTB 위클리 챌린지 3주차 — Numpy, Pandas 그리고 시각화 실습하기

Python 데이터 분석의 핵심 라이브러리인 **NumPy**, **Pandas**, **Matplotlib**, **Seaborn**, **SciPy**의 주요 개념을 실습하는 미니퀘스트 모음입니다.

---

## 프로젝트 구조

```
03/
├── numpy_quest.py        # NumPy 퀘스트 (6개 통합)
├── pandas_quest.py       # Pandas 기본 + 데이터 변환 퀘스트 (9개 통합)
├── datavisual_quest.py   # 데이터 시각화 퀘스트 (다수 통합)
├── utils/
│   └── utils.py          # 공통 출력 유틸리티
└── data/
    ├── unique_data.csv              # 중복 제거 퀘스트에서 생성되는 CSV
    └── metacritic_Toppc_games.csv   # Kaggle PC 게임 데이터셋
```

---

## numpy_quest.py

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Quest 1 | **Dimension (차원)** | `ndim`, `reshape`, `np.newaxis`로 배열 차원 다루기 |
| Quest 2 | **Shape (형태)** | `shape`, `reshape`으로 배열 형태 변환 |
| Quest 3 | **Data Type (데이터 타입)** | `dtype`, `float64`, `uint8`, `itemsize`로 자료형 다루기 |
| Quest 4 | **Indexing (인덱싱)** | 기본 인덱싱, 2D 배열 슬라이싱, 조건 기반 인덱싱 |
| Quest 5 | **Operations (연산)** | 배열 덧셈, 브로드캐스팅, 최대값 위치 탐색 |
| Quest 6 | **Universal Functions (유니버설 함수)** | `np.multiply`, `np.add`, `np.log10` 등 ufunc 활용 |

---

## pandas_quest.py

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Pandas Quest 1 | **Series** | Series 생성(리스트/딕셔너리), 인덱스 접근, `fillna`로 NaN 처리 |
| Pandas Quest 2 | **DataFrame** | 컬럼 접근, `sort_values` 정렬, 조건 필터링, 파생 컬럼 추가 |
| Data Mutation Quest 1 | **Filtering (필터링)** | 단일 조건, 복합 조건(`\|`), `query()`를 이용한 데이터 필터링 |
| Data Mutation Quest 2 | **Grouping (그룹화)** | `groupby` + `sum`, `agg(['sum','mean'])`, `filter`로 그룹 집계 |
| Data Mutation Quest 3 | **Merge (병합)** | `inner join`, `left join`, 다중 키 merge 및 `suffixes` 처리 |
| Data Mutation Quest 4 | **Missing Data (결측값 처리)** | `isnull().sum()`, `dropna()`, `fillna(mean())`으로 결측값 처리 |
| Data Mutation Quest 5 | **Pivot (피벗)** | `pivot`, `pivot_table`, 다중 값 컬럼 피벗 테이블 생성 |
| Data Mutation Quest 6 | **Duplicates Removal (중복 제거)** | `drop_duplicates`, `duplicated`, CSV 저장 및 불러오기 |
| Data Mutation Quest 7 | **String Operations (문자열 처리)** | `str.lower`, `str.strip`, `str.contains`, `str.split`으로 문자열 조작 |

### 실제 데이터 분석 (Kaggle PC 게임 데이터)

| 분석 | 주제 | 핵심 개념 |
|------|------|-----------|
| PC Game Analysis | **Metacritic 상위 PC 게임 점수 분석** | `read_csv`, `str.split().astype(float)`로 Score 파싱, `groupby('Rating')`으로 등급별 `max/min/mean` 집계, 조건 필터링으로 저점수 게임 추출 |

> **데이터 출처**: [Kaggle - Top PC Games: Metacritic vs Steam Popularity](https://www.kaggle.com/datasets/alyahmedts13/top-pc-games-metacritic-vs-steam-popularity)

---

## datavisual_quest.py

### 데이터 준비 (Data Ready)

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Data Ready Quest 1 | **Structured Data (정형 데이터)** | `df.info()`, 조건 필터링, `astype`, 날짜 기반 연봉 조정 |
| Data Ready Quest 2 | **Unstructured Data (비정형 데이터)** | `json.loads`, `re.sub`으로 텍스트 정제, 단어 개수 카운트 |

### Matplotlib 기본 시각화

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Matplotlib Basic Quest 1 | **Bar Chart (막대 그래프)** | `plt.bar`, 그룹 막대그래프, `np.arange` + `bar_width`로 나란히 배치 |
| Matplotlib Basic Quest 2 | **Histogram (히스토그램)** | `plt.hist`, 중첩 히스토그램, `cumulative=True`로 누적 히스토그램 |
| Matplotlib Basic Quest 3 | **Scatter Plot (산점도)** | `plt.scatter`, 난수 산점도, 카테고리별 색상 분류 |
| Matplotlib Basic Quest 4 | **Box Plot (박스플롯)** | `plt.boxplot`, 다중 그룹 비교, `patch_artist`로 커스텀 스타일링 |
| Matplotlib Basic Quest 5 | **Advanced Multiple Graph (고급 다중 그래프)** | `plt.subplots`, `sharex`, `gridspec.GridSpec`으로 복합 레이아웃 |
| Matplotlib Basic Quest 6 | **Venn Diagram (벤 다이어그램)** | `matplotlib_venn.venn2`, 집합 연산, 교집합 색상 조건부 변경 |

### Seaborn 기본 시각화

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Seaborn Basic Quest 1 | **Categorical Data (범주형 데이터)** | `sns.barplot`, `sns.boxplot`, `sns.violinplot` + `sns.stripplot` 오버레이 |
| Seaborn Basic Quest 2 | **Continuous Data (연속형 데이터)** | `sns.histplot(kde=True)`, `sns.lineplot`, `sns.regplot`으로 회귀선 추가 |
| Seaborn Basic Quest 3 | **Relational Data (관계형 데이터)** | `sns.scatterplot`, `sns.regplot`, `sns.pairplot`으로 다변량 관계 탐색 |

### 시계열 데이터 (Times Series Data)

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Times Series Quest 1 | **Time Series Data (시계열 데이터)** | `pd.date_range`, 누적합, 이동 평균, IQR 기반 이상치 탐지 |
| Times Series Quest 2 | **Resampling (리샘플링)** | `resample("D").mean()`, `asfreq`, `interpolate`, `min/max` 집계 |
| Times Series Quest 3 | **Moving Average (이동평균)** | `rolling(window=7).mean()` SMA, `ewm(span=7)` EMA, 이상치 필터링 |
| Times Series Quest 4 | **Financial Data (금융 데이터)** | OHLCV 데이터, `describe()`, SMA/EMA 계산, 주간 변동성(`std`) 분석 |

### SciPy 통계 분석

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| SciPy Quest 1 | **Normal Distribution (정규 분포)** | `np.random.normal`, `stats.norm.pdf`, `stats.norm.cdf`, `stats.norm.ppf` |
| SciPy Quest 2 | **Descriptive Statistics (기술 통계)** | `np.mean`, `np.median`, IQR 기반 이상치 제거, `stats.skew`, `stats.kurtosis` |
| SciPy Quest 3 | **Hypothesis Testing (가설 검정)** | `stats.ttest_ind` (t검정), `stats.chisquare` (카이제곱), `stats.f_oneway` (ANOVA) |
| SciPy Quest 4 | **Statistical Visualization (통계적 시각화)** | `boxplot` 수평 출력, KDE 겹친 히스토그램, 카이제곱 독립성 검정 + 막대그래프 |

### 시계형 데이터 입수 (Time Series Data Acquisition)

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| Time Series Quest 1 | **시계형 데이터 입수** | `sns.load_dataset("penguins")`, `sns.boxplot`으로 종별 체중 비교, `sns.scatterplot` + `hue`로 날개 길이 vs 체중 산점도 |

### 양자 회로 (Quantum Circuit)

| Quest | 주제 | 핵심 개념 |
|-------|------|-----------|
| 양자회로 Quest 1 | **Bell State (벨 상태)** | `QuantumCircuit`, Hadamard 게이트(`h`), CNOT 게이트(`cx`), `AerSimulator`로 양자 회로 시뮬레이션 |

---

## 유틸리티

### `utils/utils.py`
모든 퀘스트에서 공통으로 사용하는 출력 함수입니다.

```python
def printanswer(num: int, answer: list | str):
    # 퀘스트 번호와 결과를 포맷에 맞게 출력
```

---

## 실행 방법

```bash
# 루트 디렉토리(03/)에서 실행
python numpy_quest.py
python pandas_quest.py
python datavisual_quest.py
```

> **주의**: `utils` 모듈 경로 참조를 위해 반드시 `03/` 디렉토리에서 실행해야 합니다.

---

## 사용 라이브러리

- `numpy` — 다차원 배열 연산
- `pandas` — 데이터프레임 기반 데이터 분석
- `matplotlib` — 기본 데이터 시각화
- `matplotlib_venn` — 벤 다이어그램
- `seaborn` — 통계적 데이터 시각화
- `scipy` — 통계 분석 및 가설 검정
- `qiskit` — 양자 회로 설계 및 시뮬레이션
- `qiskit_aer` — 양자 회로 시뮬레이터 백엔드

---

## 회고

이전 위클리 챌린지에서 db사용인가 json데이터 다루는데에 pandas를 사용했었는데 이렇게 깊게 사용한 적은 처음이다. 확실히 코테에서는
이렇게 깊기 다루지도 않고 굳이 pandas를 안써도 대부분 풀 수 있는 문제이기 때문에 깊게 보지 않았던 점이 있었다. 그리고 numpy같은 경우
아직 numpy가 얼마나 더 필요한 지는 감이 안온다. 하도 코테에서 list, dict, 등 다양한걸 어떻게 풀어내는지만 연구하다가
이걸로 리스트와 dict에 유용한 함수들을 사용해보려 하니 헷갈리는 부분도 있지만 차원에 대해서 더 확인해볼 필요가 있다.
또한 go처럼 int64, int32, 데이터 유형을 더 잘게 쪼개서 데이터 타입을 정하는 것도 신선한 충격이였다. 왜냐하면 나에게 파이썬은 그냥
동적 할당과 아무렇게나 해도 기본 데이터 유형으로 저장해주는 쉬운 언어라 생각했기 때문이다. 다시 공부하려니 머리아프다.

이번 데이터 시각화 퀘스트를 통해 matplotlib, seaborn, scipy까지 다루게 되었는데 시각화 라이브러리가 이렇게 다양하고 세부적인지
몰랐다. 특히 seaborn은 matplotlib 위에서 동작하면서도 훨씬 코드가 간결해서 인상적이었다. 시계열 데이터에서 리샘플링, 이동평균,
이상치 탐지까지 다루니 실무에서 어떻게 활용되는지 감이 오기 시작했다. SciPy의 가설 검정(t검정, 카이제곱, ANOVA)은 통계 배경이
없으면 이해하기 어려운 부분이 있었지만, 코드 자체는 직관적이어서 배우는 재미가 있었다.

양자회로의 기본 개념인 벨 상태를 읽고 이해를 해보려고 했는데 벌써부터 머리가 어지럽다. 0과 1이 켜지고 끈다 혹인 있다 없다 라는 의미
밖에 없던 나의 세계에 두개가 양립한다는 사실부터 벌써 머리에서 쥐가 난다. 하나가 0이면 다른 하나도 0이고 하나가 1이면 다른 하나도 1이라는
벨 상태. 양자의 큐비트가 서로 강하게 얽혀 있다고 하여 벨 상태라고 하는데 안얽혀있다면 무엇일까. 결국 q0만 0~1 왔다갔다하고 q1은 0인 상태이니
00, 10 만 나오는거일텐데 그럼 그냥 비트랑 다를게 무엇인가. 그래서 찾아보니 결국 양자는 측정하면 컴퓨터 비트처럼 나오지만 측정전의 값이 중요하다.
그래서 컴퓨터 비트는 이미 정해진 값에서 길을 찾고 하나의 길을 탐색하지만 양자는 있지 않을 수도 있는 값부터 조사하기 때문에 가능한 길들의 파동(?) 혹은
진행방향을 찾는다고 생각하면 조금 더 이해가 쉬울 것 같다.
