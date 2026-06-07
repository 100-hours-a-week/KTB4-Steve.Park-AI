# Week 04 - ML 알고리즘 & 딥러닝 모델 탐구

> KTB 위클리 챌린지 4주차 — 머신러닝 알고리즘부터 CNN 이미지 분류까지

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1r_IMGf8xLBBksj0By6AhI2fet05S127K?usp=drive_link)

---

## 목표

PUBG 스탯 데이터셋을 통해 다양한 ML 알고리즘을 직접 구현하고 비교하며,  
마지막으로 CNN 모델을 활용한 이미지 이진 분류(고양이 vs 강아지)를 실습한다.

---

## 프로젝트 구조

```
04/
├── main.py           # 전체 알고리즘 실습 통합 파일
└── data/
    ├── Pubg_Stats.csv          # PUBG 스탯 데이터셋 (Kaggle)
    └── cat_image_*.png         # CNN 학습용 고양이 이미지
    └── dog_image_*.png         # CNN 학습용 강아지 이미지
```

---

## 데이터셋

| 항목 | 내용 |
|------|------|
| 이름 | PUBG Stats Dataset |
| 출처 | [Kaggle - mohammadtalib786/pubg-stats-dataset](https://www.kaggle.com/datasets/mohammadtalib786/pubg-stats-dataset) |
| 타겟 변수 | `Rank` (Silver / Gold / Platinum / Diamond) |
| 주요 피처 | Matches_Played, Kills, Deaths, Assists, Damage_Dealt, Headshots, Wins 등 12개 |

---

## 설치 및 실행

**의존성 설치**

```bash
pip install tensorflow tensorflow_decision_forests scikit-learn imbalanced-learn pillow requests
```

**데이터셋 다운로드**

```bash
mkdir -p data
curl -L -o data/pubg-stats-dataset.zip \
  https://www.kaggle.com/api/v1/datasets/download/mohammadtalib786/pubg-stats-dataset
unzip -o data/pubg-stats-dataset.zip -d data/
```

**실행 (Google Colab 또는 Python 환경)**

```bash
python main.py
```

---

## 알고리즘 목록

### 1. K-NN (K-Nearest Neighbors)

| 항목 | 내용 |
|------|------|
| 라이브러리 | `sklearn.neighbors.KNeighborsClassifier` |
| 하이퍼파라미터 | `n_neighbors=10` |
| 전처리 | MinMaxScaler, LabelEncoder |
| 타겟 | Rank 4분류 |

---

### 2. Perceptron (수동 구현)

| 항목 | 내용 |
|------|------|
| 구현 방식 | NumPy 기반 직접 구현 (라이브러리 미사용) |
| 활성화 함수 | Step function (z ≥ 0 → 1, else 0) |
| 타겟 | Gold / Platinum / Diamond = 1, Silver = 0 (이진) |
| 학습 | `learning_rate=0.01`, `epochs=100` |

---

### 3. SVM (Support Vector Machine)

| 항목 | 내용 |
|------|------|
| 라이브러리 | `sklearn.svm.SVC` |
| 커널 | `linear` |
| 전처리 | StandardScaler, LabelEncoder |
| 타겟 | Rank 4분류 |

---

### 4. Random Forest

| 항목 | 내용 |
|------|------|
| 라이브러리 | `tensorflow_decision_forests` |
| 모델 1 (기본) | `RandomForestModel(task=CLASSIFICATION)` |
| 모델 2 (튜닝) | `num_trees=100, max_depth=10` |
| 타겟 | Rank 4분류 (category 코드화) |
| 결과 | 기본 모델 **0.8889** (4개 알고리즘 중 최고) |

---

### 5. Naive Bayes

| 항목 | 내용 |
|------|------|
| 라이브러리 | `sklearn.naive_bayes.GaussianNB` |
| 전처리 | StandardScaler, LabelEncoder |
| 타겟 | Rank 4분류 |

---

### 6. Data Augmentation (SMOTE)

| 항목 | 내용 |
|------|------|
| 라이브러리 | `imblearn.over_sampling.SMOTE` |
| 목적 | Rank 클래스 불균형 해소 (Silver 과소 표본) |
| 방식 | 선형 보간 기반 오버샘플링 |
| 비교 알고리즘 | Random Forest |
| 결과 | 기존 0.8889 → 증강 후 **0.9625** |

**클래스 분포 변화**

```
증강 전: Diamond/Gold/Platinum 다수, Silver 소수 (불균형)
증강 후: 전체 클래스 균등 분포
```

---

### 7. 활성화 함수 비교 (ReLU / Sigmoid / Tanh)

TensorFlow 연산으로 직접 정의 후 동일한 신경망 구조에 적용하여 성능 비교

| 활성화 함수 | 수식 |
|------------|------|
| ReLU | `max(0, x)` |
| Sigmoid | `1 / (1 + e^(-x))` |
| Tanh | `(e^x - e^(-x)) / (e^x + e^(-x))` |

시각화: 활성화 함수 곡선 / Epoch별 검증 정확도 / 최종 테스트 정확도 비교

---

### 8. MLP (Multi-Layer Perceptron)

| 항목 | 내용 |
|------|------|
| 구조 | Dense(64, relu) → Dense(32, relu) → Dense(4, softmax) |
| 손실 함수 | `sparse_categorical_crossentropy` |
| 옵티마이저 | `adam` |
| 학습 | `epochs=50`, `batch_size=32` |
| 결과 | 테스트 샘플 50개 기준 **86.67%** (전체 테스트셋 정확도와 수렴) |

---

### 9. CNN (Convolutional Neural Network)

**데이터**: thecatapi.com / thedogapi.com에서 각 100장 다운로드

| 항목 | 내용 |
|------|------|
| 입력 | (64, 64, 3) RGB 이미지 |
| 레이블 | 고양이=1, 강아지=0 (이진 분류) |
| 손실 함수 | `binary_crossentropy` |
| 출력 활성화 | `sigmoid` |

**모델 구조**

| 레이어 | 출력 Shape | 파라미터 수 |
|--------|-----------|------------|
| Conv2D(32, 3×3, relu) | (62, 62, 32) | 896 |
| MaxPooling2D(2×2) | (31, 31, 32) | 0 |
| Conv2D(64, 3×3, relu) | (29, 29, 64) | 18,496 |
| GlobalAveragePooling2D | (64,) | 0 |
| Dense(64, relu) | (64,) | 4,160 |
| Dense(1, sigmoid) | (1,) | 65 |
| **합계** | | **23,617** |

**이미지 수집 방법**

```python
# ?limit=100 으로 한 번에 100개 URL을 받아 rate limit 방지
response = requests.get("https://api.thecatapi.com/v1/images/search?limit=100")
```

> 루프 내 개별 호출 방식은 rate limit으로 JSONDecodeError 발생 → `?limit=N` 방식으로 수정

---

## 알고리즘 성능 비교 (PUBG Rank 분류)

### 분류 알고리즘

| 알고리즘 | 정확도 | 비고 |
|---------|--------|------|
| Random Forest + SMOTE (기본) | **0.9625** | 최고 성능 |
| Random Forest + SMOTE (튜닝) | 0.9500 | num_trees=100, max_depth=10 |
| SVM | 0.8889 | kernel=linear |
| Random Forest (기본) | 0.8889 | |
| Random Forest (튜닝) | 0.8667 | num_trees=100, max_depth=10 |
| MLP | 0.8667 | epochs=50 |
| K-NN | 0.8667 | n_neighbors=10 |
| Naive Bayes | 0.8222 | GaussianNB |
| Perceptron | - | 이진 분류 (Gold 이상 여부) |

### 활성화 함수 비교 (MLP 기반)

| 활성화 함수 | 테스트 정확도 |
|------------|-------------|
| Tanh | **0.8667** |
| ReLU | 0.8444 |
| Sigmoid | 0.8000 |

---

## 사용 라이브러리

- `numpy`, `pandas` — 데이터 처리
- `scikit-learn` — K-NN, SVM, Naive Bayes, 전처리
- `tensorflow` / `keras` — 활성화 함수, MLP, CNN
- `tensorflow_decision_forests` — Random Forest
- `imbalanced-learn` — SMOTE 데이터 증강
- `requests`, `Pillow` — 이미지 다운로드 및 처리
- `matplotlib` — 시각화

---

## 회고

<details>
<summary><b>기획 단계</b></summary>

4주차는 머신러닝 알고리즘들을 하나씩 직접 적용해보는 과제였다. 이론으로 배운 K-NN, SVM, 랜덤 포레스트를 실제 데이터에 돌려보는 게 처음이었다. PUBG 데이터를 쓴 건 내가 실제로 오래 해본 게임이라 피처들의 의미를 직관적으로 알 수 있었기 때문이다.

</details>

<details>
<summary><b>개발 단계</b></summary>

퍼셉트론은 교재를 보고 직접 구현했는데 이게 실무에서 그대로 쓰이는 알고리즘인지 아니면 개념 이해용인지 아직 확실하지 않다. 강사님 피드백을 기다리고 있다.

SMOTE로 클래스 불균형을 맞춘 뒤 랜덤 포레스트를 돌렸더니 0.8889에서 0.9625로 정확도가 올라간 게 인상적이었다. 데이터 품질이 알고리즘 선택만큼 중요하다는 걸 체감했다.

MLP에서 테스트 샘플 20개일 때 80%, 50개로 늘렸더니 정확히 86.67%가 나왔다. AI가 샘플이 커질수록 전체 정확도(86%)에 수렴한다고 했는데 실제로 그렇게 되는 걸 보니 신기했다.

CNN 섹션에서는 외부 API를 루프로 1000번 호출하다 rate limit에 걸려 JSONDecodeError가 발생했다. `?limit=100` 파라미터로 한 번에 URL 목록을 받아오도록 수정하며 API 호출 방식에 대해 배웠다.
(사실은 어차피 colab에서 돌리면 내 데이터폴더가 아니기 때문에 많이 받아볼랬는데 api 리밋에 걸려버려서 100개로 돌렸다 ㅠ)

</details>
