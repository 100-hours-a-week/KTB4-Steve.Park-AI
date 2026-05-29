# 데이터 시각화 미니퀘스트 모음
import numpy as np
import pandas as pd
from utils.utils import printanswer
import json
import re
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib_venn import venn2
import seaborn as sns
import scipy.stats as stats
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# ============================================================
# Data Ready Quest 1 - Structured Data (정형 데이터)
# ============================================================
print("\n===== Data Ready Quest 1 - Structured Data (정형 데이터) =====")

## 1
data = {
    '이름': ['김철수', '이영희', '박민수', '최지현', '홍길동'],
    '나이': [25, 30, 35, 28, 40],
    '직업': ['개발자', '마케터', '개발자', '디자이너', 'CEO'],
    '연봉': [4000, 3500, 5000, 4200, 10000],
    '가입일': ['2020-05-21', '2019-07-15', '2021-01-10', '2018-11-03', '2017-09-27']
}

df = pd.DataFrame(data)

print("#1 Quest:")
print(df.info())
print()
# printanswer(1, answer)

## 2
data = {
    '이름': ['김철수', '이영희', '박민수', '최지현', '홍길동', '정지훈', '이지은'],
    '나이': [25, 30, 35, 28, 40, 50, 22],
    '직업': ['개발자', '마케터', '개발자', '디자이너', 'CEO', '디자이너', '마케터'],
    '연봉': [4000, 3500, 5000, 4200, 10000, 4600, 3300],
    '가입일': ['2020-05-21', '2019-07-15', '2021-01-10', '2018-11-03', '2017-09-27', '2016-04-11', '2022-03-19']
}

df = pd.DataFrame(data)

df = df[(df['나이'] >= 30) & (df['연봉'] <= 5000)]

printanswer(2, df)

## 3
data = {
    '이름': ['김철수', '이영희', '박민수', '최지현', '홍길동', '정지훈', '이지은'],
    '나이': [25, 30, 35, 28, 40, 50, 22],
    '직업': ['개발자', '마케터', '개발자', '디자이너', 'CEO', '디자이너', '마케터'],
    '연봉': [4000, 3500, 5000, 4200, 10000, 4600, 3300],
    '가입일': ['2020-05-21', '2019-07-15', '2021-01-10', '2018-11-03', '2017-09-27', '2016-04-11', '2022-03-19']
}

df = pd.DataFrame(data)
df['연봉'] = df['연봉'].astype(float)
df.loc[df['가입일'].str[:4].astype(int) <= 2019, '연봉'] *= 1.1

salarymean = df['연봉'].mean()

printanswer(3, salarymean)

# ============================================================
# Data Ready Quest 2 - Unstructured Data (비정형 데이터)
# ============================================================
print("\n===== Data Ready Quest 2 - Unstructured Data (비정형 데이터) =====")

## 1
data = '''
[
    {"이름": "김철수", "나이": 25, "직업": "개발자", "연봉": 4000},
    {"이름": "이영희", "나이": 30, "직업": "마케터", "연봉": 3500},
    {"이름": "박민수", "나이": 35, "직업": "디자이너", "연봉": 4200}
]
'''

data = json.loads(data)

df = pd.DataFrame(data)

printanswer(1, df)

## 2
text = "안녕하세요!!! 저는 AI 모델-입니다. 12345 데이터를   정리해 보겠습니다."

dftext = re.sub(r"[^가-힣\s]", '', text)
dftext2 = re.sub(r"\s+", ' ', dftext).strip()

printanswer(2, dftext2)

## 3
text = "자연어 처리는 재미있다. 파이썬과 pandas를 활용하면 편리하다. 데이터 분석은 흥미롭다."

texts = text.split(". ")
df = pd.DataFrame({"문장": texts})
df['단어개수'] = df['문장'].str.split(" ").str.len()

printanswer(3, df)

# ============================================================
# Matplotlib Basic Quest 1 - Bar Chart Data (막대 그래프)
# ============================================================
print("\n===== Matplotlib Basic Quest 1 - Bar Chart Data (막대 그래프) =====")

## 1
categories = ['A', 'B', 'C', 'D', 'E']
values = [12, 25, 18, 30, 22]

plt.cla()
plt.bar(categories, values, color='#abcdef')
plt.xlabel("Categories")
plt.ylabel("Value")
plt.title("Matplotlib Basic Quest 1-1 - Bar Chart Data")

plt.show()

## 2
categories = ['A', 'B', 'C', 'D', 'E']
values_2023 = [10, 15, 20, 25, 30]
values_2024 = [5, 10, 12, 18, 22]

x = np.arange(len(categories))

plt.cla()
plt.bar(x, values_2023, color='#abcdef', label='2023')
plt.bar(x, values_2024, color='#fedcba', label='2024')

plt.xticks(x, categories)
plt.xlabel('Category')
plt.ylabel("Value")
plt.title("Matplotlib Basic Quest 1-2 - Bar Chart Data")

plt.legend()
plt.show()

## 3
departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance']
performance_2023 = [80, 70, 90, 60, 75]
performance_2024 = [85, 75, 95, 65, 80]

bar_width = 0.4

x = np.arange(len(departments))

plt.cla()
plt.bar(x - bar_width/2, performance_2023, width=bar_width, color='#abcdef', label='2023')
plt.bar(x + bar_width/2, performance_2024, width=bar_width, color='#fedcba', label='2024')

plt.xticks(x, departments)
plt.xlabel('Department')
plt.ylabel("Performance")
plt.title("Matplotlib Basic Quest 1-3 - Bar Chart Data")

plt.legend()
plt.show()

# ============================================================
# Matplotlib Basic Quest 2 - Histogram (히스토그램)
# ============================================================
print("\n===== Matplotlib Basic Quest 2 - Histogram (히스토그램) =====")

## 1
data = np.random.randn(1000)

plt.cla()
plt.hist(data, bins=15, color='#abcdef', edgecolor='#000000')
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.title("Matplotlib Basic Quest 2-1 - Histogram")

plt.show()

## 2
data1 = np.random.randn(1000)
data2 = np.random.randn(1000) + 3

plt.cla()
plt.hist(data1, bins=15, alpha=0.5, color='#abcdef', edgecolor='#000000')
plt.hist(data2, bins=15, alpha=0.5, color='#fedcba', edgecolor='#000000')
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.title("Matplotlib Basic Quest 2-2 - Histogram")

plt.show()

## 3
data = np.random.randn(1000)

plt.cla()
plt.hist(data, bins=15, cumulative=True, color='#abcdef', edgecolor='#000000')
plt.xlabel("Value")
plt.ylabel("Cumulative Frequency")
plt.title("Matplotlib Basic Quest 2-3 - Histogram")

plt.show()

# ============================================================
# Matplotlib Basic Quest 3 - Scatter Plot (산점도)
# ============================================================
print("\n===== Matplotlib Basic Quest 3 - Scatter Plot (산점도) =====")

## 1
x = [1, 2, 3, 4, 5]
y = [3, 1, 4, 5, 2]

plt.cla()
plt.scatter(x, y, color='#abcdef', marker='o')
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Matplotlib Basic Quest 3-1 - Scatter Plot")

plt.show()

## 2
np.random.seed(42)
x = np.random.rand(50) * 10  # 0~10 범위의 난수 50개
y = np.random.rand(50) * 10  # 0~10 범위의 난수 50개
colordata = np.random.rand(3)
alphavalue = np.random.rand()

plt.cla()
plt.scatter(x, y, color=colordata, alpha=alphavalue, marker='o')
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Matplotlib Basic Quest 3-2 Scatter Plot")

plt.show()

## 3
np.random.seed(10)
x = np.random.randn(50) * 2
y = np.random.randn(50) * 2
categories = np.random.choice(['A', 'B', 'C'], size=50)

colordata = np.random.rand(3, 3)
colors = {'A': colordata[0],'B': colordata[1],'C': colordata[2]}

plt.cla()
for cat in np.unique(categories):
    idx = categories == cat
    plt.scatter(x[idx], y[idx],
        color=colors[cat],
        label=f'Category {cat}',
        alpha=0.7
    )

plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Matplotlib Basic Quest 3-3 Scatter Plot")
plt.legend()

plt.show()

# ============================================================
# Matplotlib Basic Quest 4 - Box Plot (박스플롯)
# ============================================================
print("\n===== Matplotlib Basic Quest 4 - Box Plot (박스플롯) =====")

## 1
np.random.seed(42)
data = np.random.randn(50)

plt.cla()

plt.boxplot(data)
plt.title("Matplotlib Basic Quest 4-1 - Box Plot")
plt.ylabel("Values")

plt.show()

## 2
np.random.seed(42)
group_a = np.random.randn(50) * 1.5  # 표준편차 1.5, 평균 0
group_b = np.random.randn(50) * 1.5 + 3  # 표준편차 1.5, 평균 3
group_c = np.random.randn(50) * 1.5 - 3  # 표준편차 1.5, 평균 -3

plt.cla()
plt.boxplot([group_a, group_b, group_c], tick_labels=['Group 1', 'Group 2', 'Group 3'])
plt.xlabel("Groups")
plt.ylabel("Values")
plt.title("Matplotlib Basic Quest 4-2 - Box Plot")

plt.show()

## 3
np.random.seed(42)
group_x = np.random.randn(50) * 2  # 표준편차 2, 평균 0
group_y = np.random.randn(50) * 2 + 5  # 표준편차 2, 평균 5

plt.cla()
plt.boxplot([group_x, group_y], tick_labels=['Group X', 'Group Y'], patch_artist=True, 
            boxprops=dict(facecolor="#abcdef", color="#fedcba"),
            capprops=dict(color="orange", linewidth=3),
            medianprops=dict(color="#000000", linewidth=2),
            flierprops=dict(marker='o', markerfacecolor='red', markersize=10, linestyle='none'))
plt.xlabel("Groups")
plt.ylabel("Values")
plt.title("Matplotlib Basic Quest 4-3 - Box Plot")

plt.show()

# ============================================================
# Matplotlib Basic Quest 5 - Advanced Multiple Graph (고급 다중 그래프)
# ============================================================
print("\n===== Matplotlib Basic Quest 5 - Advanced Multiple Graph (고급 다중 그래프) =====")

## 1
x = np.linspace(-5, 5, 100)
y1 = x ** 2  # x의 제곱
y2 = x ** 3  # x의 세제곱

plt.close()

fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8,6))

axes[0].plot(x, y1, color='#abcdef', label='x^2')
axes[0].set_title("Matplotlib Basic Quest 5-1 - Advanced Multiple Graph\nX^2")
axes[0].set_xlabel("X-axis")
axes[0].set_ylabel("Y-axis")
axes[0].legend()

axes[1].plot(x, y2, color='#fedcba', label='x^3')
axes[1].set_title("X^3")
axes[1].set_xlabel("X-axis")
axes[1].set_ylabel("Y-axis")
axes[1].legend()

plt.tight_layout()

plt.show()

## 2
normal_data = np.random.randn(1000)  # 정규 분포 난수 1000개
uniform_data = np.random.rand(1000)  # 균등 분포 난수 1000개

plt.close()

fig, axes = plt.subplots(2, 1, sharex=True, figsize=(8,6))

axes[0].boxplot(normal_data)
axes[0].set_title("Matplotlib Basic Quest 5-2 - Advanced Multiple Graph\nNormal Rand")
axes[0].set_ylabel("Values")

axes[1].boxplot(normal_data)
axes[1].set_title("Uniform Rand")
axes[1].set_ylabel("Values")

plt.tight_layout()

plt.show()

## 3
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.random.randn(100)
categories = ['A', 'B', 'C', 'D', 'E']
values = [3, 7, 5, 2, 8]

plt.close()

#선 그래프, 산점도, 막대 그래프, 히스토그램을
fig = plt.figure(figsize=(10, 8))
gs = gridspec.GridSpec(3, 2, figure=fig)

ax1 = fig.add_subplot(gs[0,:])
ax1.plot(x, y1, color='orange', label='Sin(x)')
ax1.set_title("Matplotlib Basic Quest 5-3 - Advanced Multiple Graph\nSine Function")
ax1.legend()

ax2 = fig.add_subplot(gs[1,0])
ax2.scatter(x, y2, color='yellow', marker='o')
ax2.set_title("Scatter random nums 100")

ax3 = fig.add_subplot(gs[1,1])
ax3.hist(y2, bins=20, color='blue', edgecolor='black')
ax3.set_xlabel("Value")
ax3.set_ylabel("Frequency")
ax3.set_title("Histogram with Rand 100")

ax4 = fig.add_subplot(gs[2,:])
ax4.bar(categories, values, color='gray')
ax4.set_xlabel("Categories")
ax4.set_ylabel("Values")
ax4.set_title("Categories Bar Graph")

plt.tight_layout()

plt.show()

# ============================================================
# Matplotlib Basic Quest 6 - Venn Diagram (벤다이어그램)
# ============================================================
print("\n===== Matplotlib Basic Quest 6 - Venn Diagram (벤다이어그램) =====")

## 1
set_A = {"사과", "바나나", "체리", "망고"}
set_B = {"바나나", "망고", "포도", "수박"}

plt.close()

venn2([set_A, set_B], set_labels=("Set A", "Set B"))

plt.title("Matplotlib Basic Quest 6-1 - Venn Diagram")

plt.show()

answerlist = [f"A: {set_A-set_B}", f"B: {set_B-set_A}"]

printanswer(1, answerlist)

## 2
set_A = {"사과", "바나나", "체리", "망고"}
set_B = {"바나나", "망고", "포도", "수박"}
set_C = {"망고", "수박", "딸기", "오렌지"}

avalues = set_A - set_B - set_C
bvalues = set_B - set_A - set_C
cvalues = set_C - set_A - set_B

andvalues = set_A & set_B & set_C

answerlist= [f"각 요소:\nA:{avalues}\nB:{bvalues}\nC:{cvalues}", f"A n B n C: {andvalues}"]

printanswer(2, answerlist)

## 3
set_A = {"사과", "바나나", "체리", "망고"}
set_B = {"바나나", "망고", "포도", "수박"}

plt.close()

diagram = venn2([set_A, set_B], set_labels=['Set A', 'Set B'])
plt.title("Matplotlib Basic Quest 6-3 - Venn Diagram")

if len(set_A & set_B) >= 2:
    diagram.get_patch_by_id("11").set_color("yellow")

plt.show()

# ============================================================
# Seaborn Basic Quest 1 - Categorical Data (범주형 데이터)
# ============================================================
print("\n===== Seaborn Basic Quest 1 - Categorical Data (범주형 데이터) =====")

## 1
data = pd.DataFrame({
    "Category": ["X", "X", "Y", "Y", "Z", "Z", "Z", "X", "Y", "Z"],
    "Values": [5, 9, 4, 6, 12, 10, 14, 7, 5, 18]
})

plt.close()
sns.barplot(x="Category", y="Values", data=data)

plt.title("Seaborn Basic Quest 1-1 - Categorical Data")

plt.show()

##2
data = pd.DataFrame({
    "group": ["A", "A", "B", "B", "C", "C", "C", "A", "B", "C"],
    "score": [65, 70, 55, 60, 90, 85, 95, 72, 58, 88]
})

plt.close()

sns.boxplot(x="group", y="score", data=data)

plt.title("Seaborn Basic Quest 1-2 - Categorical Data")

plt.show()

## 3
data = pd.DataFrame({
    "category": ["A", "A", "B", "B", "C", "C", "C", "A", "B", "C"],
    "score": [80, 85, 70, 75, 95, 90, 100, 82, 72, 98]
})

plt.close()

sns.violinplot(x='category', y='score', data=data)
sns.stripplot(x='category', y='score', data=data, jitter=True)

plt.title("Seaborn Basic Quest 1-3 - Categorical Data")

plt.show()

# ============================================================
# Seaborn Basic Quest 2 - Continuous Data (연속형 데이터)
# ============================================================
print("\n===== Seaborn Basic Quest 2 - Continuous Data (연속형 데이터) =====")

## 1
np.random.seed(42)
data = np.random.randn(500)

plt.close()

sns.histplot(data, bins=20, color='#abcdef', kde=True)

plt.xlabel("Values")
plt.ylabel("Frequency")
plt.title("Seaborn Basic Quest 2-1 - Continuous Data")

plt.show()

## 2
x = np.linspace(0, 20, 100)
y = np.sin(x)

plt.close()

sns.lineplot(x=x, y=y, color='orange')

plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Seaborn Basic Quest 2-2 - Continuous Data")

plt.show()

## 3
np.random.seed(0)
x = np.random.rand(100) * 10  # 0~10 사이 난수
y = 2 * x + np.random.randn(100)  # x와 비례하는 관계, 약간의 변동 추가

plt.close()

sns.regplot(x=x, y=y, color='green')

plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Seaborn Basic Quest 2-3 - Continuous Data')

plt.show()

# ============================================================
# Seaborn Basic Quest 3 - Relational Data (관계형 데이터)
# ============================================================
print("\n===== Seaborn Basic Quest 3 - Relational Data (관계형 데이터) =====")

## 1
tips = sns.load_dataset("tips")

plt.close()

plt.figure(figsize=(6, 5))
sns.scatterplot(x="total_bill", y="tip", data=tips, color="#abcdef")

plt.xlabel("Total Bills ($)")
plt.ylabel("Tip ($)")
plt.title("Seaborn Basic Quest 3-1 - Relational Data")

plt.show()

## 2
tips = sns.load_dataset("tips")

plt.close()

df = pd.DataFrame(tips)
df = df[df['sex'] == 'Male']

sns.regplot(x="total_bill", y="tip", data=df, color="#abcdef", scatter_kws={'alpha':0.3}, line_kws={'color':'red'})

plt.xlabel("Total Bills ($)")
plt.ylabel("Tip ($)")
plt.title("Seaborn Basic Quest 3-2 - Relational Data")

plt.show()

## 3
tips = sns.load_dataset("tips")

plt.close()

df = pd.DataFrame(tips)
df = df.drop(columns=['smoker', 'time'])

graph = sns.pairplot(df, vars=["total_bill", "tip", "size"], palette='coolwarm',
             hue="day")

graph.fig.suptitle("Seaborn Basic Quest 3-3 - Relational Data", y=1)
plt.show()

# ============================================================
# Times Series Data Quest 1 - Time Series Data (시계열 데이터)
# ============================================================
print("\n===== Times Series Data Quest 1 - Time Series Data (시계열 데이터) =====")

## 1
np.random.seed(42)
date_range = pd.date_range(start="2023-01-01", periods=100, freq="D")  # 100일간의 날짜 생성
values = np.cumsum(np.random.randn(100))  # 랜덤 값의 누적합

plt.close()

df = pd.DataFrame({"Date":date_range, "Values":values})

sns.lineplot(x="Date", y="Values", data=df, color="#abcdef", marker='o')
plt.xlabel("Date")
plt.ylabel("Value")
plt.title("Times Series Data Quest 1-1 - Time Series Data")
plt.xticks(rotation=45)

plt.show()

## 2
np.random.seed(42)
date_range = pd.date_range(start="2023-01-01", periods=100, freq="D")
values = np.cumsum(np.random.randn(100))

plt.close()

df = pd.DataFrame({"Date":date_range, "Values":values})
df["Moving_Avg"] = df["Values"].rolling(window=7).mean()

sns.lineplot(x="Date", y="Values", data=df, label="Original Data", color="black")
sns.lineplot(x="Date", y="Moving_Avg", data=df, label="Changed Data", color="orange")

plt.xlabel("Date")
plt.ylabel("Value")
plt.title("Times Series Data Quest 1-2 - Time Series Data")
plt.xticks(rotation=45)
plt.legend()

plt.show()

## 3
np.random.seed(42)
date_range = pd.date_range(start="2023-01-01", periods=100, freq="D")
values = np.cumsum(np.random.randn(100))

plt.close()

df = pd.DataFrame({"Date":date_range, "Values":values})

q1 = df["Values"].quantile(0.25)
q3 = df["Values"].quantile(0.75)
iqr = q3 - q1
k = 0.5
lower_bound = q1 - k * iqr
upper_bound = q3 + k * iqr

df["Outliner"] = (df["Values"] < lower_bound) | (df["Values"] > upper_bound)

outliners = df[df["Outliner"]]
sns.lineplot(x="Date", y="Values", data=df, label="Original Data", color="black")
sns.scatterplot(x="Date", y="Values", data=outliners, label="Outliners", color="red", s=100)

plt.xlabel("Date")
plt.ylabel("Value")
plt.title("Times Series Data Quest 1-3 - Time Series Data")
plt.xticks(rotation=45)
plt.legend()

plt.show()

# ============================================================
# Times Series Data Quest 2 - Resampling (리샘플링)
# ============================================================
print("\n===== Times Series Data Quest 2 - Resampling (리샘플링) =====")

## 1
date_rng = pd.date_range(start="2024-01-01", end="2024-01-05", freq="3h")

df = pd.DataFrame({
    "datetime": date_rng,
    "value": np.random.randint(10, 100, size=len(date_rng))
})

df.set_index("datetime", inplace=True)

df_daily = df.resample("D").mean()

printanswer(1, df_daily.head())

## 2
date_rng = pd.date_range(start="2024-01-01", end="2024-01-03", freq="3h")

plt.close()

df = pd.DataFrame({
    "datetime": date_rng,
    "value": np.random.randint(10, 100, size=len(date_rng))
})

df.set_index("datetime", inplace=True)

df_hourly = df.resample("h").asfreq()
df_hourly_interp = df_hourly.interpolate(method="linear")

plt.plot(df.index, df["value"], marker='o', linestyle='-', label='Original (3H)', alpha=0.7)
plt.plot(df_hourly.index, df_hourly["value"], marker='h', linestyle='--', label='Original (1H)', alpha=0.8)
plt.plot(df_hourly_interp.index, df_hourly_interp["value"], color='red', linestyle=':', label='Original (Interpolate)')

plt.xlabel("Date")
plt.ylabel("Value")
plt.title("Times Series Data Quest 2-2 - Resampling")
plt.xticks(rotation=45)
plt.grid()
plt.legend()

plt.show()

## 3
date_rng = pd.date_range(start="2024-01-01", end="2024-01-07", freq="3h")

df = pd.DataFrame({
    "datetime": date_rng,
    "value": np.random.randint(10, 100, size=len(date_rng))
})

df.set_index("datetime", inplace=True)

df_down = df.resample("D")
df_min = df_down.min()
df_max = df_down.max()

answerlist = [str(df_min.head()), str(df_max.head())]
printanswer(3, answerlist)

# ============================================================
# Times Series Data Quest 3 - Moving Average (이동평균)
# ============================================================
print("\n===== Times Series Data Quest 3 - Moving Average (이동평균) =====")

## 1
date_rng = pd.date_range(start="2024-01-01", end="2024-01-20", freq="D")
df = pd.DataFrame({
    "datetime": date_rng,
    "value": np.random.randint(50, 150, size=len(date_rng))
})

df["SMA"] = df["value"].rolling(window=7).mean()

printanswer(1, df)

## 2
# 샘플 시계열 데이터 생성
date_rng = pd.date_range(start="2024-01-01", end="2024-01-20", freq="D")
df = pd.DataFrame({
    "datetime": date_rng,
    "value": np.random.randint(50, 150, size=len(date_rng))
})

df["EMA"] = df["value"].ewm(span=7, adjust=False).mean()
df["차이"] = df["EMA"] - df["value"]

printanswer(2, df)

## 3
# 샘플 시계열 데이터 생성
date_rng = pd.date_range(start="2024-01-01", end="2024-01-20", freq="D")
df = pd.DataFrame({
    "datetime": date_rng,
    "value": np.random.randint(50, 150, size=len(date_rng))
})

df["SMA"] = df["value"].rolling(window=7).mean()
df = df[(abs((df["value"] - df["SMA"]) / df["SMA"])) >= 0.2]

printanswer(3, df)

# ============================================================
# Times Series Data Quest 4 - Financial Data (금융 데이터) 
# ============================================================
print("\n===== Times Series Data Quest 4 - Financial Data (금융 데이터) =====")

## 1
# 샘플 금융 데이터 생성
data = {
    'Date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
    'Open': [100, 102, 105, 103, 108, 107, 110, 112, 115, 118],
    'High': [102, 106, 108, 107, 110, 109, 112, 115, 117, 120],
    'Low': [98, 100, 103, 101, 106, 105, 108, 110, 113, 116],
    'Close': [101, 104, 106, 105, 109, 108, 111, 113, 116, 119],
    'Volume': [1000, 1200, 1500, 1300, 1600, 1400, 1700, 1800, 1900, 2000]
}

df = pd.DataFrame(data)

printanswer(1, df)
printanswer(1, str(df.describe()))

## 2
data = {
    'Date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
    'Close': [101, 104, 106, 105, 109, 108, 111, 113, 116, 119]
}

df = pd.DataFrame(data)

df["SMA_5"] = df["Close"].rolling(window=5).mean()
df["EMA_5"] = df["Close"].ewm(span=5, adjust=False).mean()

printanswer(2, df)

## 3
# 샘플 금융 데이터 생성 (30일치)
date_rng = pd.date_range(start='2024-01-01', periods=30, freq='D')
close_prices = np.random.uniform(100, 200, size=len(date_rng))  # 100~200 사이의 랜덤 종가 생성

df = pd.DataFrame({"Close":close_prices}, index=date_rng)

df_weekly = df.resample("W").agg({"Close":"mean"})
df_weekly["Volatility"] = df_weekly["Close"].rolling(window=2).std()

printanswer(3, df_weekly)

# ============================================================
# SciPy Quest 1 - 정규 분포 (Normal Distribution)
# ============================================================
print("\n===== SciPy Quest 1 - 정규 분포 (Normal Distribution) =====")

## 1
data = np.random.normal(loc=60, scale=15, size=500)

data.sort()

meand = np.mean(data)
stdd = np.std(data)
mind = min(data)
maxd = max(data)

answer = f"mean: {meand}\nstandard dev: {stdd}\nmin: {mind}\nmax: {maxd}"

printanswer(1, answer)

## 2
x_value = 65
pdf_value = stats.norm.pdf(x_value, loc=50, scale=10)

answer = f"f({x_value}) = {pdf_value}"

printanswer(2, answer)

## 3
x_value = 80
cdf_value = stats.norm.cdf(x_value, loc=70, scale=8)
quantile_95 = stats.norm.ppf(0.95, loc=70, scale=8)

answer = f"cdf: f({x_value}) = {cdf_value:.4f}\nppf: 95th percentile = {quantile_95:.2f}"

printanswer(3, answer)

# ============================================================
# SciPy Quest 2 - 기술 통계(Descriptive Statistics)
# ============================================================
print("\n===== SciPy Quest 2 - 기술 통계(Descriptive Statistics) =====")

## 1
np.random.seed(42)
data = np.random.normal(loc=50, scale=10, size=100)  # 평균 50, 표준편차 10인 정규 분포 데이터 생성
df = pd.DataFrame(data, columns=["value"])

mean_value = np.mean(df["value"])
median_value = np.median(df["value"])

printanswer(1, f"mean: {mean_value}\nmedian: {median_value}")

## 2
np.random.seed(42)
data = np.random.normal(loc=50, scale=10, size=100)  # 평균 50, 표준편차 10인 정규 분포 데이터 생성
df = pd.DataFrame(data, columns=["value"])

q1 = np.percentile(df["value"], 25)
q3 = np.percentile(df["value"], 75)
iqr = q3 - q1

lower_bound = q1 - 1.5 * iqr
upper_bound = 93 + 1.5 * iqr

original_mean = np.mean(df["value"])
df = df[(df["value"] >= lower_bound) & (df["value"] <= upper_bound)]
changed_mean = np.mean(df["value"])

answer = f"original mean: {original_mean}\nchanged_mean: {changed_mean}"

printanswer(2, answer)

## 3
np.random.seed(42)
data = np.random.normal(loc=50, scale=10, size=100)  # 평균 50, 표준편차 10인 정규 분포 데이터 생성
df = pd.DataFrame(data, columns=["value"]) 

skewness = stats.skew(df["value"])
kurtosis = stats.kurtosis(df["value"])

answer = f"왜도: {skewness}\n첨도: {kurtosis}"

printanswer(3, answer)

# ============================================================
# SciPy Quest 3 - 가설 검정 (Hypothesis Testing)
# ============================================================
print("\n===== SciPy Quest 3 - 가설 검정 (Hypothesis Testing) =====")

## 1
np.random.seed(42)
sample_data = np.random.normal(loc=50, scale=5, size=30)  # 평균 50, 표준편차 5인 데이터 30개 생성
changed_data = np.random.normal(loc=52, scale=5, size=30)  # 평균 50, 표준편차 5인 데이터 30개 생성

df = pd.DataFrame({'Group A': sample_data, 'Group B' : changed_data})
t_stat, p_value = stats.ttest_ind(sample_data, changed_data)

if p_value < 0.05:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 유의미"
else:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 무의미"    

printanswer(1, answer)

## 2
# 관측된 데이터 (Observed)
observed = np.array([50, 60, 90])

# 기대값 (Expected)
expected = np.array([66, 66, 66]) * (observed.sum() / np.sum([66, 66, 66]))

statistic, p_value = stats.chisquare(observed, expected)

if p_value < 0.05:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 유의미"
else:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 무의미"    

printanswer(2, answer)

## 3
np.random.seed(42)
group_1 = np.random.normal(loc=50, scale=10, size=30)  # 평균 50, 표준편차 10
group_2 = np.random.normal(loc=55, scale=10, size=30)  # 평균 55, 표준편차 10
group_3 = np.random.normal(loc=60, scale=10, size=30)  # 평균 60, 표준편차 10

statistic, p_value = stats.f_oneway(group_1, group_2, group_3)

if p_value < 0.05:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 유의미"
else:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 무의미"    

printanswer(3, answer)

# ============================================================
# SciPy Quest 4 - 통계적 시각화(Statistical Visualization)
# ============================================================
print("\n===== SciPy Quest 4 - 통계적 시각화(Statistical Visualization) =====")

## 1
# 데이터 생성 (평균=70, 표준편차=20인 정규 분포 데이터 1000개)
np.random.seed(42)
data = np.random.normal(loc=70, scale=20, size=1000)

plt.close()

df = pd.DataFrame(data, columns=["value"])
plt.boxplot(df["value"], vert=False, patch_artist=True)
plt.title("SciPy Quest 4-1 - Statistical Visualization")
plt.xlabel("Value")
plt.grid(axis="x", linestyle="--", alpha=0.7)

plt.show()

## 2
# 데이터 생성
np.random.seed(42)
group_A = np.random.normal(loc=55, scale=8, size=200)  # 평균 55, 표준편차 8
group_B = np.random.normal(loc=60, scale=8, size=200)  # 평균 60, 표준편차 8

plt.close()

df = pd.DataFrame({"group_A":group_A, "group_B":group_B})
sns.histplot(df["group_A"], bins=30, kde=True, color="blue", alpha=0.7)
sns.histplot(df["group_B"], bins=30, kde=True, color="orange", alpha=0.7)

plt.title("SciPy Quest 4-2 - Statistical Visualization")
plt.xlabel("Value")
plt.ylabel("Density")

plt.show()

t_stat, p_value = stats.ttest_ind(group_A, group_B)

if p_value < 0.05:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 유의미"
else:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 무의미"    

printanswer(2, answer)

## 3
# 데이터 생성 (광고 A와 B의 클릭 여부)
observed_data = pd.DataFrame({
    "Ad_A": [120, 380],  # 광고 A 클릭(120명) vs 미클릭(380명)
    "Ad_B": [150, 350]   # 광고 B 클릭(150명) vs 미클릭(350명)
}, index=["Click", "No Click"])

plt.close()

# 카이제곱 검정 수행
chi2_stat, p_value, dof, expected = stats.chi2_contingency(observed_data)  # 독립성 검정을 위한 카이제곱 검정 수행

if p_value < 0.05:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 유의미"
else:
    answer = f"p_value: {p_value}\np_value < 0.05 = {p_value < 0.05} -> 평균 차이 무의미"    

printanswer(3, answer)

sns.barplot(x=observed_data.columns, y=observed_data.loc["Click"], hue=observed_data.columns, palette=["blue", "orange"], legend=False)
plt.title("SciPy Quest 4-3 - Statistical Visualization")
plt.xlabel("Group")
plt.ylabel("Clicked Amount")

plt.show()

# ============================================================
# Time Series Quest 1 - 시계형 데이터 입수
# ============================================================
print("\n===== Time Series Quest 1 - 시계형 데이터 입수 =====")

## 1
penguins = sns.load_dataset("penguins")

plt.close()

plt.figure(figsize=(6, 5))
sns.boxplot(x="species", y="body_mass_g", data=penguins)

plt.xlabel("Species")
plt.ylabel("Body Mass")
plt.title("Penguin Species vs Body Mass")

plt.show()

## 2
penguins = sns.load_dataset("penguins")

plt.close()

df = pd.DataFrame(penguins)

sns.scatterplot(x="flipper_length_mm", y="body_mass_g", data=df, color="#abcdef", hue="species")

plt.xlabel("Flipper Length")
plt.ylabel("Body Mass")
plt.title("Time Penguin Data #2")

plt.show()

# ============================================================
# 양자회로 퀘스트
# ============================================================
print("\n===== 양자 회로 퀘스트 =====")

###
# 컴퓨터 비트는 0 또는 1 가능
# 양자 비트는 0과 1이 동시에 가능
# 이 상태를 Quantum Superposition이라한다. 뭐냐 이게

# 벨 상태 만들기
plt.close()

qc = QuantumCircuit(2) # 두개의 큐비트 생성

qc.h(0) # 0번 큐비트에 H게이트 적용 -> Hadamard게이트 추가라고 하는거고 이때 H가 적용되고나서 0일 확률 50%, 1일 확류 50%이 되고 측정되기 전까진 둘 다 될 수 있다.
qc.cx(0, 1) # CNOT 게이트 -> p0가 1이면 p1 뒤집기 -> 그래서 q0가 00이면 그대로 갈꺼고 10이면 11로 변경될꺼다. 그래서 00과 11 둘다 50%인 것. 10, 01이 안나오는 이유는 양자 두개가 강하게 얽혀있기 때문
qc.measure_all() # 맨 마지막에 측정기를 단다

qc.draw("mpl")

simulator = AerSimulator()
job = simulator.run(qc, shots=1000)
result = job.result()
counts = result.get_counts()

plt.show()

## 그래서 이 코드의 뜻은 두 큐비트를 얽힌 상태, 즉 벨 상태로 만든 뒤에 측정하면 항상 같은 값이 나오도록 설계한 양자 회로라고 할 수 있다.