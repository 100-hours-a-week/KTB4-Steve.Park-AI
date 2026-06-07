# Install tensorflow_decision_forests to resolve the ModuleNotFoundError.
# This library is used later in the Random Forest section.

# If you didn't install tensorflow_decision_forests, please execute next code
!pip install tensorflow_decision_forests

# Data Augmentataion 실행 시 오류 나면 해당 코드를 실행
!pip install imbalanced-learn

The user provided a `curl` command to download the dataset from Kaggle. I will use this to get the data into the environment.

# Download the dataset from Kaggle
# Ensure you have a 'data' directory for consistency with the original code.

# If you don't have this file, please download it
!mkdir -p data
!curl -L -o data/pubg-stats-dataset.zip https://www.kaggle.com/api/v1/datasets/download/mohammadtalib786/pubg-stats-dataset

# Unzip the downloaded dataset
!unzip -o data/pubg-stats-dataset.zip -d data/

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler as mms, StandardScaler
from sklearn.model_selection import train_test_split as tts
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

import tensorflow as tf
from tensorflow import keras
import tensorflow_decision_forests as tfdf

from imblearn.over_sampling import SMOTE

from copy import deepcopy

# 배틀그라운드 스탯 정보 출처 : https://www.kaggle.com/datasets/mohammadtalib786/pubg-stats-dataset
original_data = pd.read_csv("data/Pubg_Stats.csv")

Now that the `tensorflow_decision_forests` library is installed and the dataset is downloaded and extracted, the original data loading cell should work as expected.

##############################
#       데이터 전처리           #
##############################
original_data = original_data.dropna()
original_data = original_data.drop(columns=['Player_Name', 'Unnamed: 0'])

numeric_cols = [
    'Matches_Played', 'Kills', 'Deaths', 'Assists', 'Damage_Dealt',
    'Headshots', 'Wins', 'Top_10s', 'Revives', 'Distance_Traveled',
    'Weapons_Used', 'Time_Survived'
]

# NA데이터 모두 제거
df = deepcopy(original_data)

# 데이터 정규화 (0과 1 사이 값으로 스케일링)
scaler = mms()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

# 데이터 원-핫 인코딩 -> 플레이어 이름은 불필요
# df = pd.get_dummies(df, columns=['Player_Name'])

# 데이터 분할
# 학습용 60% 검증용 20% 테스트용 20%
learning_df, temp_df = tts(df, test_size=0.4, random_state=42)
validation_df, test_df = tts(temp_df, test_size=0.5, random_state=42)

##############################
#       K-NN 알고리즘          #
##############################

df = deepcopy(original_data)

# 데이터 정하기
X = df.drop(columns=['Rank'])

# Rank가 문자열이기 떄문에 인코딩을 해야한다
le = LabelEncoder()
y = le.fit_transform(df['Rank'])

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)

scaler = mms()

# 스케일링
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# KNN 모델 적용해보기
model = KNeighborsClassifier(n_neighbors=10)
model.fit(X_train, y_train)

# 평가
accuracy = model.score(X_test, y_test)

print("---  K-NN Algorithm Test ---")
print(f"PUBG Stats Rank Accuracy : {accuracy}")

# 샘플 데이터 예측
sample = X_test[0].reshape(1, -1)
prediction = model.predict(sample)

## 예측을 데이터에 맞게 해야했는데 나는 string -> int로 변경해서 다시 롤백하는 작업이 필요하다.
# predicted_rank = y[prediction[0]]
predicted_rank = le.inverse_transform([prediction[0]])

print(f"예측된 랭크 첫 번 째 테스트 샘플 : {predicted_rank}")
print()

# 얘의 분포도가 궁금해져서 그림을 그려보기로 했다.
# 점수는 배틀그라운에서 오래해본 내가 중요도로 생각하는 가중치를 각자 임시로 주었다
df['Score'] = (
    df['Kills'] * 5 +
    df['Damage_Dealt'] +
    df['Wins'] * 10 +
    df['Top_10s'] * 8
)

for rank in df['Rank'].unique():
    temp = df[df['Rank'] == rank]

    plt.scatter(
        temp['Score'],
        temp['Matches_Played'],
        label=rank,
        s=5,
        alpha=0.7
    )

plt.xlabel("Score")
plt.ylabel("Matches Played")
plt.legend()
plt.show()

# 실버 하나가 튀어나와있긴 한데 나머지가 다이아라서 가중치 문제인 것 같다.
# 이걸 해결 하려면 가중치를 좀 조절해야겠다.
# 가중치 조절하는건 나중에 해보자.


##############################
#       Perceptron           #
##############################
# 퍼셉트론이 이렇게 작동하게 되는건지 확실하게 모르겠습니다. 강사님이 확인하신다면 해당 코드에 대해서 피드백 해주시면 감사하겠습니다.
# 교재를 보고 비슷하게 구현을 하였습니다. 이해는 되긴하지만 실제로 구현할때 이 알고리즘을 사용하는지, 혹은 다른 알고리즘 사용으로
# 이 알고리즘은 그냥 이해하고 넘어가면 되는지도 궁금합니다.

df = deepcopy(original_data)

X = df.drop(columns=['Rank'])
X = X.values

y = (df['Rank'].isin(['Gold', 'Platinum', 'Diamond'])).astype(int)
y = y.values

X_train, X_test, y_train, y_test = tts(
    X, y,
    test_size=0.2,
    random_state=42
)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

weights = np.zeros(X_train.shape[1])
bias = 0

learning_rate = 0.01
epochs = 100

for epoch in range(epochs):
    for x, target in zip(X_train, y_train):
        # 선형 결합
        z = np.dot(x, weights) + bias

        # 활성화 함수 (step function)
        prediction = 1 if z >= 0 else 0

        # 오차
        error = target - prediction

        # 가중치 업데이트
        weights += learning_rate * error * x

        # 바이어스 업데이트
        bias += learning_rate * error

def predict(X):

    z = np.dot(X, weights) + bias

    return np.where(z >= 0, 1, 0)

predictions = predict(X_test)

print("---  Perceptron Algorithm Test ---")
print(f"PUBG Stats Rank Weights : {weights}")
print(f"PUBG Stats Rank Bias : {bias}")
print(f"예측된 출력 : {predictions}")
print()

##############################
#           SVM              #
##############################

df = deepcopy(original_data)

X = df.drop(columns=['Rank'])

# Rank가 문자열이기 떄문에 인코딩을 해야한다
le = LabelEncoder()
y = le.fit_transform(df['Rank'])

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

svm_model = SVC(kernel='linear')
svm_model.fit(X_train, y_train)

accuracy = svm_model.score(X_test, y_test)

print("---  SVM Algorithm Test ---")
print(f"PUBG Stats Rank Accuracy : {accuracy}")

# 샘플 데이터 예측
# 위에서 K-NN 알고리즘에서 사용했는데 여기 있을 줄이야...
sample = X_test[0].reshape(1, -1)
prediction = svm_model.predict(sample)
predicted_rank = le.inverse_transform([prediction[0]])

print(f"예측된 랭크 첫 번 째 테스트 샘플 : {predicted_rank}")
print()

##############################
#       Random Forest        #
##############################

df = deepcopy(original_data)

df['Rank'] = df['Rank'].astype('category').cat.codes

# 데이터 정하기
X = df.drop(columns=['Rank'])

# Rank가 문자열이기 떄문에 인코딩을 해야한다
y = df['Rank']

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)

# TensorFlow 데이터셋 변환
# 음 기존에는 됬지만 텐서플로우 데이터셋으로 변환하려고 concat을 사용하였는데 Pandas DataFrame과 NumArray를 더할 수 없다고한다.
# 따라서 pd.Series로 시리즈로 변환한 뒤에 concat을 해준다.
train_data = tfdf.keras.pd_dataframe_to_tf_dataset(pd.concat([X_train, y_train], axis=1), label="Rank")
test_data = tfdf.keras.pd_dataframe_to_tf_dataset(pd.concat([X_test, y_test], axis=1), label="Rank")

############################
# 기존에 하던대로 했더니 오류가 나서 다시 교재를 참고했더니 Rank를 카테고리화하는 부분 자체가 잘못되어 있었다. 그래서 카테고리화를 다시 한뒤에
# 실행을 하니 문제 없이 진행되어서 아래에서 체크하는 AI의 결과인 결측값 확인은 더이상 필요가 없어졌다.

# TensorFlow 데이터셋 변환 전에 데이터프레임에서 결측값(NaN) 확인

# # X_train과 y_train을 합쳐 전체 훈련 데이터프레임을 생성
# train_df_for_check = pd.concat([X_train, pd.Series(y_train, name="Rank")], axis=1)
# print(f"Total NaNs in training DataFrame before TF Dataset conversion: {train_df_for_check.isnull().sum().sum()}")

# # X_test와 y_test를 합쳐 전체 테스트 데이터프레임을 생성
# test_df_for_check = pd.concat([X_test, pd.Series(y_test, name="Rank")], axis=1)
# print(f"Total NaNs in testing DataFrame before TF Dataset conversion: {test_df_for_check.isnull().sum().sum()}")

# # 개별 구성 요소에서도 확인 (만약을 대비해)
# print(f"NaNs in X_train: {X_train.isnull().sum().sum()}")
# print(f"NaNs in y_train: {pd.Series(y_train).isnull().sum()}")
# print(f"NaNs in X_test: {X_test.isnull().sum().sum()}")
# print(f"NaNs in y_test: {pd.Series(y_test).isnull().sum()}")
############################

# Random Forest 모델 학습
model1 = tfdf.keras.RandomForestModel(task=tfdf.keras.Task.CLASSIFICATION)
model1.compile(metrics=["accuracy"])
model1.fit(train_data)

# 하이퍼파라미터 튜닝된 Random Forest 모델 학습
model2 = tfdf.keras.RandomForestModel(task=tfdf.keras.Task.CLASSIFICATION, num_trees=100, max_depth=10)
model2.compile(metrics=["accuracy"])
model2.fit(train_data)

# 모델 평가
eval1 = model1.evaluate(test_data, return_dict=True)
eval2 = model2.evaluate(test_data, return_dict=True)

print("---  Random Forest Algorithm Test ---")
print(f"PUBG Stats Rank Basic Model Accuracy : {eval1.get('accuracy', 'N/A'):.4f}")
print(f"PUBG Stats Rank Tunned Model Accuracy (num_trees=100, max_depth=10): {eval2.get('accuracy', 'N/A'):.4f}")

# 예측 결과
pred1 = model1.predict(test_data)[:5]
pred2 = model2.predict(test_data)[:5]

print(f"PUBG Stats Rank Basic Model Prediction Top 5 : {pred1.flatten()}")
print(f"PUBG Stats Rank Tunned Model Prediction Top 5 : {pred2.flatten()}")

print()

##############################
#       Naive Bayes          #
##############################

df = deepcopy(original_data)

X = df.drop(columns=['Rank'])

# Rank가 문자열이기 떄문에 인코딩을 해야한다
le = LabelEncoder()
y = le.fit_transform(df['Rank'])

# 위의 Random Forest와 동일하게 카테고리화를 하려했으나 핫인코딩이 안되어있으면 string이 남는 문제 때문에
# 핫인코딩을 진행하여 다시 테스트 데이터를 가공하였다.
X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

nb_model = GaussianNB()
nb_model.fit(X_train, y_train)

accuracy = nb_model.score(X_test, y_test)

print("---  Naive Bayes Algorithm Test ---")
print(f"PUBG Stats Rank Accuracy : {accuracy:.4f}")

sample = X_test[0].reshape(1, -1)
prediction = nb_model.predict(sample)
predicted_rank = le.inverse_transform([prediction[0]])

print(f"예측된 랭크 첫 번 째 테스트 샘플 : {predicted_rank}")
print()

##############################
#       Data Augmentation    #
##############################

# 기존 데이터와 비교할 증강 데이터에서 사용할 알고리즘은 Random Forest를 사용해봐야겠다. 위의 4개 알고리즘을 돌려보았을때
# 정확도는 Random Forest가 0.8889 로 가장 높다. 지금까지 사용한 기준으로는
# Random Forest > SVM > K-NN = Naive Bayes   열외: Perceptron

# 찾아보니 SMOTE라는 좋은 시스템이 있다. 이걸 통해서 클래스간 불균형을 우선 맞추자.
# 이건 노이즈를 추가하는게 아닌 단순한 선형보간 후 샘플링을 하여 데이터를 증강시키는 방법이다.
# 우선 없으면 상위의 "# Data Augmentataion 실행 시 오류 나면 해당 코드를 실행" 코드를 실행하자.

df = deepcopy(original_data)

df['Rank'] = df['Rank'].astype('category').cat.codes

# 데이터 정하기
X = df.drop(columns=['Rank'])
y = df['Rank']

smote = SMOTE(random_state=42)
X_aug, y_aug = smote.fit_resample(X, y)

# 아래의 결과를 보면 기존에는 실버의 클래스가 매우 적고 나머지 상위 3개 티어의 클래스는 50개 이상으로 불균형이 심했다.
# 위의 Smote코드를 진행한 후에는 동일하게 모두 100개로 맞추어 졌다.
rank_cat = original_data['Rank'].astype('category')

print("Rank 순서 및 매핑:")
print(rank_cat.cat.categories)
print(y.value_counts())
print(y_aug.value_counts())

# 이렇게 생성하고 다시 Random Forest 알고리즘을 사용해 비슷한지 한번 확인해보자.
X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)
X_aug_train, X_aug_test, y_aug_train, y_aug_test = tts(X_aug, y_aug, test_size=0.2, random_state=42)

# TensorFlow 데이터셋 변환
train_data = tfdf.keras.pd_dataframe_to_tf_dataset(pd.concat([X_train, y_train], axis=1), label="Rank")
test_data = tfdf.keras.pd_dataframe_to_tf_dataset(pd.concat([X_test, y_test], axis=1), label="Rank")

train_aug_data = tfdf.keras.pd_dataframe_to_tf_dataset(pd.concat([X_aug_train, y_aug_train], axis=1), label="Rank")
test_aug_data = tfdf.keras.pd_dataframe_to_tf_dataset(pd.concat([X_aug_test, y_aug_test], axis=1), label="Rank")

# Random Forest 모델 학습
model1 = tfdf.keras.RandomForestModel(task=tfdf.keras.Task.CLASSIFICATION)
model1.compile(metrics=["accuracy"])
model1.fit(train_data)

model_aug_1 = tfdf.keras.RandomForestModel(task=tfdf.keras.Task.CLASSIFICATION)
model_aug_1.compile(metrics=["accuracy"])
model_aug_1.fit(train_aug_data)

# 하이퍼파라미터 튜닝된 Random Forest 모델 학습
model2 = tfdf.keras.RandomForestModel(task=tfdf.keras.Task.CLASSIFICATION, num_trees=100, max_depth=10)
model2.compile(metrics=["accuracy"])
model2.fit(train_data)

model_aug_2 = tfdf.keras.RandomForestModel(task=tfdf.keras.Task.CLASSIFICATION, num_trees=100, max_depth=10)
model_aug_2.compile(metrics=["accuracy"])
model_aug_2.fit(train_aug_data)

# 모델 평가
eval1 = model1.evaluate(test_data, return_dict=True)
eval2 = model2.evaluate(test_data, return_dict=True)

eval_aug_1 = model_aug_1.evaluate(test_aug_data, return_dict=True)
eval_aug_2 = model_aug_2.evaluate(test_aug_data, return_dict=True)

print("---  Data Augmentation Test ---")
print("Original Data :: ")
print(f"PUBG Stats Rank Basic Model Accuracy : {eval1.get('accuracy', 'N/A'):.4f}")
print(f"PUBG Stats Rank Tunned Model Accuracy (num_trees=100, max_depth=10): {eval2.get('accuracy', 'N/A'):.4f}")
print()
print("Data Augmentation Applied Data :: ")
print(f"PUBG Stats Rank Basic Model Accuracy : {eval_aug_1.get('accuracy', 'N/A'):.4f}")
print(f"PUBG Stats Rank Tunned Model Accuracy (num_trees=100, max_depth=10): {eval_aug_2.get('accuracy', 'N/A'):.4f}")
print()

# 해당 코드를 실행하면 우선 기존의 데이터는 0.8889로 정확도가 그대로 인걸 볼 수 있다.
# 기존 데이터를 증강한 데이터를 Random Forest 알고리즘으로 돌린 결과, 0.9625라는 더 높은 정확도를 보여준다.
# 이를 토대로 데이터가 균일하게 분포되어 정리되어있으면 좀 더 정확한 결과를 낼 수 있다는 걸 알 수 있다.

# 예측 결과
pred1 = model1.predict(test_data)[:5]
pred2 = model2.predict(test_data)[:5]

pred_aug_1 = model_aug_1.predict(test_aug_data)[:5]
pred_aug_2 = model_aug_2.predict(test_aug_data)[:5]

print("Original Data :: ")
print(f"PUBG Stats Rank Basic Model Prediction Top 5 : {pred1.flatten()}")
print(f"PUBG Stats Rank Tunned Model Prediction Top 5 : {pred2.flatten()}")
print()
print("Data Augmentation Applied Data :: ")
print(f"PUBG Stats Rank Basic Model Prediction Top 5 : {pred_aug_1.flatten()}")
print(f"PUBG Stats Rank Tunned Model Prediction Top 5 : {pred_aug_2.flatten()}")

print()

# 이제 예측 데이터를 뽑아보면 처음에는 0 1 2 3으로 이루어진 클래스중 0번(다이아)가 높은걸로 나와 있지만 3번째
# 데이터에서는 클래스 1번과 3번에서 헷갈리는걸 알 수 있다. 여기서 확신도가 낮아지는 걸 알 수 있으며 튜닝된 모델에서도 그렇게
# 차이가 많이 나지 않는걸 알 수 있다.

# 그럼 증강된 데이터가 괜찮은가 보면 처음은 1번째 클래스가 높다가 갑자기 3번쨰 샘플에서 0번쨰인지 1번쨰인지 헷갈린다.
# 이로써 증강된 데이터에서도 튜닝된다해도 크게 차이는 없다는걸 알 수 있다. 그래도 샘플이 적던 이전 데이터보다는
# 데이터가 헷갈리는 일이 적거나 확률이 낮다는 걸 알 수 있다.


##############################
#       활성화 함수          #
##############################

df = deepcopy(original_data)

le = LabelEncoder()

X = df[numeric_cols].values
y = le.fit_transform(df['Rank'])

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

num_classes = len(np.unique(y))

# 1. 활성화 함수 직접 정의 (tf 연산 사용 → Keras 레이어에 직접 전달 가능)
def relu(x):
    return tf.maximum(0.0, x)

def sigmoid(x):
    return 1.0 / (1.0 + tf.exp(-x))

def tanh(x):
    return (tf.exp(x) - tf.exp(-x)) / (tf.exp(x) + tf.exp(-x))

# 2. 신경망 학습
def build_and_train(activation_fn):
    model = keras.Sequential([
        keras.layers.Dense(64, activation=activation_fn, input_shape=(X_train.shape[1],)),
        keras.layers.Dense(32, activation=activation_fn),
        keras.layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
    _, test_acc = model.evaluate(X_test, y_test, verbose=0)

    return history, test_acc

histories = {}
test_results = {}

print("---  Activation Function Test ---")
for name, fn in [('ReLU', relu), ('Sigmoid', sigmoid), ('Tanh', tanh)]:
    history, acc = build_and_train(fn)
    histories[name] = history
    test_results[name] = acc
    print(f"[{name}] 테스트 정확도: {acc:.4f}")

print()

# 3. 시각화
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 활성화 함수 곡선
x_range = np.linspace(-5, 5, 200)
axes[0].plot(x_range, relu(x_range), label='ReLU', color='blue')
axes[0].plot(x_range, sigmoid(x_range), label='Sigmoid', color='green')
axes[0].plot(x_range, tanh(x_range), label='Tanh', color='red')
axes[0].axhline(0, color='gray', linewidth=0.5)
axes[0].axvline(0, color='gray', linewidth=0.5)
axes[0].set_title('Activation Funtion')
axes[0].legend()

# Epoch별 검증 정확도
colors = {'ReLU': 'blue', 'Sigmoid': 'green', 'Tanh': 'red'}
for name, history in histories.items():
    axes[1].plot(history.history['val_accuracy'], label=name, color=colors[name])
axes[1].set_title('Epoch Accuracy')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Accuracy')
axes[1].legend()

# 최종 테스트 정확도 비교
bars = axes[2].bar(test_results.keys(), test_results.values(), color=['blue', 'green', 'red'])
axes[2].set_title('Each Activation Function\'s Final Accuracy')
axes[2].set_ylabel('Accuracy')
axes[2].set_ylim(0, 1)
for bar, acc in zip(bars, test_results.values()):
    axes[2].text(bar.get_x() + bar.get_width()/2, acc + 0.01, f'{acc:.4f}', ha='center')

plt.tight_layout()
plt.show()

##############################
#       MLP 모델             #
##############################

df = deepcopy(original_data)

le = LabelEncoder()

X = df[numeric_cols].values
y = le.fit_transform(df['Rank'])

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

mlp_pubg = keras.Sequential([
    keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(len(np.unique(y)), activation='softmax')
])

mlp_pubg.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
history = mlp_pubg.fit(X_train, y_train, epochs=50, batch_size=32,
                        validation_split=0.2, verbose=0)

_, pubg_acc = mlp_pubg.evaluate(X_test, y_test, verbose=0)
print("---  MLP Model Test ---")
print(f"\n PUBG Stats Accuracy: {pubg_acc:.4f}")
print()

# 이게 맞을까 궁금해서 예측결과를 한번 뽑아보았다. 확률이 가장 높은 클래스가 실제로 맞는지 확인해보자.
sample_X = X_test[:20]
pred_probs = mlp_pubg.predict(sample_X, verbose=0)  # 각 클래스 확률
pred_classes = np.argmax(pred_probs, axis=1)         # 가장 높은 확률 클래스
pred_ranks = le.inverse_transform(pred_classes)       # 숫자 → Silver/Gold/...
actual_ranks = le.inverse_transform(y_test[:20])

for i in range(len(actual_ranks)):
    print(f"실제: {actual_ranks[i]:<10} | 예측: {pred_ranks[i]:<10} | 확률: {pred_probs[i].max():.2%}")

total = sum([1 if actual_ranks[i] == pred_ranks[i] else 0 for i in range(len(actual_ranks))])/ len(actual_ranks)

print(f"정확도 : {total:.2%}")
print()

# 정확도가 80%로 나오는데 음... 너무 적게 잡아서 그렇겠지.. 다수의 집합을 테스트해보면 저렇게 올라가는걸까 물어보자
# AI말로도 많이 근접해질거라고 한다. 현재는 딱 맞는 데이터를 비교해서 80%로 떨어지지만 숫자가 커지면 커질 수록 86%에 근접할 거라고 한다.
# 20개 까지 늘렸을때는 80%였지만 50개라면 어떤지 보자.
sample_X = X_test[:50]
pred_probs = mlp_pubg.predict(sample_X, verbose=0)  # 각 클래스 확률
pred_classes = np.argmax(pred_probs, axis=1)         # 가장 높은 확률 클래스
pred_ranks = le.inverse_transform(pred_classes)       # 숫자 → Silver/Gold/...
actual_ranks = le.inverse_transform(y_test[:50])

for i in range(len(actual_ranks)):
    print(f"실제: {actual_ranks[i]:<10} | 예측: {pred_ranks[i]:<10} | 확률: {pred_probs[i].max():.2%}")

total = sum([1 if actual_ranks[i] == pred_ranks[i] else 0 for i in range(len(actual_ranks))])/ len(actual_ranks)

#소름 돋게도 50개까지 늘리니 바로 86.67%가 나온다.
print(f"정확도 : {total:.2%}")

print()

##############################
#       CNN 모델             #
##############################

import requests
from PIL import Image
from io import BytesIO

cat_images = []
dog_images = []

# ?limit=N 으로 한 번의 API 호출에 N개 URL을 받아옴 (rate limit 방지)
# API 무료 플랜 최대치: 100개
def fetch_images(api_url, count):
    images = []
    remaining = count
    while remaining > 0:
        batch = min(remaining, 100)
        response = requests.get(f"{api_url}?limit={batch}")
        if response.status_code != 200 or not response.text.strip():
            print(f"API 응답 오류: status={response.status_code}, 재시도 중...")
            continue
        for item in response.json():
            try:
                img_response = requests.get(item["url"])
                img = Image.open(BytesIO(img_response.content)).convert("RGB").resize((64, 64))
                images.append(np.array(img) / 255.0)
            except Exception:
                pass  # 개별 이미지 오류는 건너뜀
        remaining -= batch
    return images

print("고양이 이미지 다운로드 중...")
cat_images = fetch_images("https://api.thecatapi.com/v1/images/search", 100)
print("강아지 이미지 다운로드 중...")
dog_images = fetch_images("https://api.thedogapi.com/v1/images/search", 100)

X = np.array(cat_images + dog_images)
y = np.array([1] * len(cat_images) + [0] * len(dog_images))  # 고양이: 1, 강아지: 0

print(f"--- CNN Model Test ---")
print(f"이미지 데이터 shape: {X.shape}")

# --- 학습/테스트 분할 ---
X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2, random_state=42)

# --- CNN 모델 정의 ---
cnn_model = keras.Sequential([
    keras.Input(shape=(64, 64, 3)),            # 경고 제거용
    keras.layers.Conv2D(32, (3, 3), activation='relu'),
    keras.layers.MaxPooling2D(2, 2),
    keras.layers.Conv2D(64, (3, 3), activation='relu'),
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

cnn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

cnn_model.summary()

# --- 학습 ---
history = cnn_model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=1)

# --- 평가 ---
_, test_acc = cnn_model.evaluate(X_test, y_test, verbose=0)
print(f"\n테스트 정확도: {test_acc:.4f}")

# --- 예측 ---
sample = X_test[0:1]                          # 이미지 1장
prob = cnn_model.predict(sample, verbose=0)[0][0]
label = "고양이" if prob >= 0.5 else "강아지"
print(f"예측: {label} (확률: {prob:.4f})")