from tensorflow.keras.applications import ResNet50, VGG16
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Flatten, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical, image_dataset_from_directory
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications.vgg16 import preprocess_input as vgpi
from tensorflow.keras.layers import Dropout
import tensorflow as tf

from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split, ParameterSampler
from scipy.stats import uniform

import os
import random
import numpy as np
import requests
from PIL import Image
from io import BytesIO

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

###############################
#         ResNet Model        #
###############################

# 이전에 CNN을 학습할 때 사용했던 고양이/강아지 이미지를 이용해서 ResNet 모델 학습을 진행해보자.
# 무료로 가져올수있는게 100장이니 100장까지 가져와보자
cat_images = []
dog_images = []

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
                img = Image.open(BytesIO(img_response.content)).convert("RGB").resize((224, 224))
                images.append(preprocess_input(np.array(img, dtype=np.float32)))
            except Exception as e:
                print(f"이미지 오류: {e}")  # item['url'] → e 로 변경
                pass  # 개별 이미지 오류는 건너뜀
        remaining -= batch
    return images

print("고양이 이미지 다운로드 중...")
cat_images = fetch_images("https://api.thecatapi.com/v1/images/search", 100)
print("강아지 이미지 다운로드 중...")
dog_images = fetch_images("https://api.thedogapi.com/v1/images/search", 100)

X = np.array(cat_images + dog_images)
y = np.array([1] * len(cat_images) + [0] * len(dog_images))  # 고양이: 1, 강아지: 0

num_classes = 2
input_shape = (224, 224, 3)

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)

base_model = ResNet50(weights=None, include_top=False, input_shape=input_shape)

model = Sequential()
model.add(base_model)
model.add(GlobalAveragePooling2D())
model.add(Dense(256, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, epochs=10, validation_split=0.1)

loss, accuracy = model.evaluate(x_test, y_test)
print("--- ResNet Base Model Test ---")
print(f"ResNetTest loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- Resnet Test ---
ResNetTest loss: 2.3057711124420166
Test accuracy: 0.5

이미지를 1~100개 했을때 다 이렇게나온다.
AI에게 분석을 맡겨보니 restnet모델을 불러올 때 weights 이 None이라 그렇단다.
현재 들고있는 100장의 이미지로만 패턴을 학습할 수 없다.
그럼 imagenet을 사용한다면 어떻게 된다? 전이학습을 사용하기 떄문에 사전학습된 가중치를 내 데이터로 미세조정한다.
그럼 데이터가 적을 수록 imagenet이 유리한가? 테스트해보자.
"""

second_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
second_model.trainable = False  # 사전학습 가중치 보존, 마지막 레이어만 학습

model = Sequential()
model.add(second_model)
model.add(GlobalAveragePooling2D())
model.add(Dense(256, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, epochs=10, validation_split=0.1)

loss, accuracy = model.evaluate(x_test, y_test)
print("--- ResNet ImageNet Weight Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
second_model.trainable = False  사전학습 가중치 보존, 마지막 레이어만 학습 해당 코드를 안넣었을 때
사전학습 가중치를 덮어써버리면서 학습해서 오히려 망가지면서 loss가 늘어났다.
--- ResNet ImageNet Weight Test ---
ResNetTest loss: 1.0967519283294678
Test accuracy: 0.5

위의 trainable = False 코드를 추가했을때의 결과. 확실히 loss도 줄어들고 정확도도 올라간게 확연히 보인다.
--- ResNet ImageNet Weight Test ---
Test loss: 0.5618461966514587
Test accuracy: 0.75

따라서 weights=None일때는
랜덤 초기화 -> 100장 데이터로 노이즈 학습을 하게되고 모델이 잘못된 방향으로 예측을 자신있게 하면서 loss가 높아진다.
weights='imagenet'이기만 할때는
이미 학습한 가중치를 사용하지만 100장의 데이터로 인해 학습에 오염을 일으켜서 loss가 커짐
trainable = False를 추가하게 되면 ResNet의 레이어는 동결시키고 Dense레이어에서만 학습하기때문에 loss가 확연히 줄어든다.
"""

###############################
#         VGG16 Model         #
###############################

# 아까와 똑같은 고양이/강아지 이미지 세트를 사용하자.
# 하지만 기존의 이미지를 썼다가는 resnet전용 processInput을 사용하기 때문에 vgg16꺼로 변경해야한다.

def fetch_images_vgg(api_url, count):
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
                img = Image.open(BytesIO(img_response.content)).convert("RGB").resize((224, 224))
                images.append(vgpi(np.array(img, dtype=np.float32)))
            except Exception as e:
                print(f"이미지 오류: {e}")  # item['url'] → e 로 변경
                pass  # 개별 이미지 오류는 건너뜀
        remaining -= batch
    return images

cat_images.clear()
dog_images.clear()

print("고양이 이미지 다운로드 중...")
cat_images = fetch_images_vgg("https://api.thecatapi.com/v1/images/search", 100)
print("강아지 이미지 다운로드 중...")
dog_images = fetch_images_vgg("https://api.thedogapi.com/v1/images/search", 100)

X = np.array(cat_images + dog_images)
y = np.array([1] * len(cat_images) + [0] * len(dog_images))  # 고양이: 1, 강아지: 0

num_classes = 2
input_shape = (224, 224, 3)

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)

base_model = VGG16(weights=None, include_top=False, input_shape=input_shape)

model = Sequential()
model.add(base_model)
model.add(GlobalAveragePooling2D())
model.add(Dense(256, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, epochs=10, validation_split=0.1)

loss, accuracy = model.evaluate(x_test, y_test)
print("--- VGG16 Base Model Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- VGG16 Base Model Test ---
Test loss: 1.572526216506958
Test accuracy: 0.25

얘는 0.25가 나온다. loss율은 1.57로 생각보다 높게 나온다. 그럼 왜 0.25일까 한번 분석해보자.
분석해보니 ResNet은 잘못된 학습을 해서 loss율이 높은거고 VGG16은 아예 학습을 못했다고 한다.
0.9^16 = 0.185 정도 되니 레이어를 통과할 수록 gradient가 사라지면서 gradient vanishing 현상이 발생하여
출력에 거의 도달하지 못한다. 따라서 학습율이 낮다.
그럼 위랑 똑같이 weight를 줘보자.
"""

second_model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)
second_model.trainable = False  # 사전학습 가중치 보존, 마지막 레이어만 학습

model = Sequential()
model.add(second_model)
model.add(GlobalAveragePooling2D())
model.add(Dense(256, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, epochs=10, validation_split=0.1)

loss, accuracy = model.evaluate(x_test, y_test)
print("--- VGG16 Second Model Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- VGG16 Second Model Test ---
Test loss: 0.19788140058517456
Test accuracy: 0.75

음 더 loss가 낮아지긴 했다.
그럼 epoch를 30으로 늘려서 한번 해보자
"""

third_model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)
third_model.trainable = False  # 사전학습 가중치 보존, 마지막 레이어만 학습

model = Sequential()
model.add(third_model)
model.add(GlobalAveragePooling2D())
model.add(Dense(256, activation='relu'))
model.add(Dense(num_classes, activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, epochs=30, validation_split=0.1)

loss, accuracy = model.evaluate(x_test, y_test)
print("--- VGG16 Third Model Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- VGG16 Third Model Test ---
Test loss: 0.05300433561205864
Test accuracy: 1.0

loss가 0.05로 더 낮아지는 현상이 발생했다.
epoch만 늘리니 확 줄어드는게 확인이된다.
"""

fourth_model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)
fourth_model.trainable = False  # 사전학습 가중치 보존, 마지막 레이어만 학습

model = Sequential()
model.add(fourth_model)
model.add(GlobalAveragePooling2D())
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))                   # 50% 랜덤 비활성화로 과적합 방지
model.add(Dense(num_classes, activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, epochs=10, validation_split=0.1)

loss, accuracy = model.evaluate(x_test, y_test)
print("--- VGG16 Fourth Model Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- VGG16 Fourth Model Test ---
Test loss: 0.05300433561205864
Test accuracy: 1.0

loss가 0.05로 더 낮아지는 현상이 발생했다.
epoch만 늘리니 확 줄어드는게 확인이된다.
근데 뒤늦게 깨달은게 있다.ㅁ닏랴ㅓㅁㄴㄷ랴ㅓㅁㄴㄷ;ㅣ랴ㅓㅁㄴㄷㄹ

저기 위에서 이미지를 랜덤으로 뽑아온다. 그럼? 학습도 다시 될테고 추측/예측 모두 새로이 된다.
그럼 이 수치들은 고정이 되는게 아니라 재실행할때마다 바뀔 수 밖에 없다. 이를 고정 시키려면 동일한 이미지들을 사용하거나
모델을 아예 초기화하고 다시 학습시켜야하는 방법이 있을 것 같다. 그 외에 더 있으려나? 랜덤시드고정?
"""

###############################
#         ResNet vs VGG16     #
###############################

"""
그럼 위에서 학습한대로 데이터셋을 고정시키고 ResNet이랑 VGG16 모델의 학습 성능차이를 비교해보자
Kaggle에서 가위바위보 데이터셋을 가져와서 한번 학습을 시켜보자.
"""
# 해당 코드를 통해서 데이터를 다운받고 zip 풀자
# !/bin/bash
# ! kaggle datasets download glushko/rock-paper-scissors-dataset
# ! unzip -q -o rock-paper-scissors-dataset.zip -d rock_paper_scissors

# Define paths to the dataset
base_dir = 'rock_paper_scissors/'
train_dir = os.path.join(base_dir, 'train')
val_dir = os.path.join(base_dir, 'val')

# Image parameters
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32

# Load training data
train_ds = image_dataset_from_directory(
    train_dir,
    labels='inferred',
    label_mode='categorical',
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    interpolation='nearest',
    batch_size=BATCH_SIZE,
    shuffle=False,
    seed=SEED
)

# Load validation data
val_ds = image_dataset_from_directory(
    val_dir,
    labels='inferred',
    label_mode='categorical',
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    interpolation='nearest',
    batch_size=BATCH_SIZE,
    shuffle=False
)

# Get class names
class_names = train_ds.class_names
num_classes = len(class_names)
print(f"Class names: {class_names}")
print(f"Number of classes: {num_classes}")

# Function to apply VGG16 preprocessing
def apply_vgg_preprocessing(image, label):
    image = tf.cast(image, tf.float32)
    return vgpi(image), label

# Function to apply ResNet50 preprocessing
def apply_resnet_preprocessing(image, label):
    image = tf.cast(image, tf.float32)
    return preprocess_input(image), label

# Apply ResNet50 preprocessing by default (can be changed later for VGG16)
rs_train = train_ds.map(apply_resnet_preprocessing).cache().prefetch(buffer_size=tf.data.AUTOTUNE)
rs_test = val_ds.map(apply_resnet_preprocessing).cache().prefetch(buffer_size=tf.data.AUTOTUNE)

vgg_train = train_ds.map(apply_vgg_preprocessing).cache().prefetch(buffer_size=tf.data.AUTOTUNE)
vgg_test = val_ds.map(apply_vgg_preprocessing).cache().prefetch(buffer_size=tf.data.AUTOTUNE)

# ResNet 모델
resnet_base = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
resnet_base.trainable = False

resnet_model = Sequential()
resnet_model.add(resnet_base)
resnet_model.add(GlobalAveragePooling2D())
resnet_model.add(Dense(256, activation='relu'))
resnet_model.add(Dense(num_classes, activation='softmax'))

resnet_model.compile(optimizer=Adam(learning_rate=0.001),
                     loss='categorical_crossentropy',
                     metrics=['accuracy'])

resnet_model.fit(rs_train, epochs=10, validation_data=rs_test)

loss, accuracy = resnet_model.evaluate(rs_test)
print("--- ResNet Model Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- ResNet Model Test ---
Test loss: 0.8026123046875
Test accuracy: 0.6815920472145081
"""

# VGG16 모델
vgg_base = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
vgg_base.trainable = False

vgg_model = Sequential()
vgg_model.add(vgg_base)
vgg_model.add(GlobalAveragePooling2D())
vgg_model.add(Dense(256, activation='relu'))
vgg_model.add(Dense(num_classes, activation='softmax'))

vgg_model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

vgg_model.fit(vgg_train, epochs=10, validation_data=vgg_test)

loss, accuracy = vgg_model.evaluate(vgg_test)
print("--- VGG16 Model Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- VGG16 Model Test ---
Test loss: 0.7224048972129822
Test accuracy: 0.68034827709198
"""

"""
이번엔 데이터셋을 고정하려고 가위바위보 데이터셋을 다운로드 받아 ResNet과 VGG16 모델을 비교해보았다.
이를 고정시키기 위해서 데이터를 불러올때도 shuffle을 안하게했고 seed도 42를 박아서 고정시켰다.
자 아래에는 결과가 있다.

--- ResNet Model Test ---
Test loss: 0.8026123046875
Test accuracy: 0.6815920472145081

--- VGG16 Model Test ---
Test loss: 0.7224048972129822
Test accuracy: 0.68034827709198

이를 비교해보았을때 ResNet이 VGG보다 엄청 미미하게 정확도는 높지만 loss 또한 높다.
이걸 잘 모르겠어서 한 번 검색해보았더니 ResNet모델은 자신있게 예측하고 틀리지만 VGG는 애매하게 예측해서 애매하게 맞거나 틀리는
현상이 있다고 한다.
그래서 정확도 및 loss율이 ResNet이 VGG보다 높다.
이걸 모델 캘리브레이션이라고 지칭하며 ResNet이 더 과감한 모델인 것을 알 수 있었다.
하지만 데이터가 많아지면 어떻게될지도 궁금하다.

이것도 확인해보니 데이터가 많아진다면
ResNet은 틀리는 경우도 적어지기 때문에
자신있게 틀리는 비율이 줄어들고 맞는 비율이 늘기 때문에 accuracy는 늘고 loss는 낮아진다.

그럼 VGG 는 512차원의 한계에 부딪혀서 어느 순간 학습이 개선이 안된다.
그래서 결국에는 ResNet이 VGG보다 데이터가 많다는 기준하에 더 loss가 낮아지고 accuracy는 높아질 것이라고 예상된다.

Alex 강사님에게 데이터 셋을 고정시키는게 중요한지 여쭈어보았다.
데이터 셋을 "고정"한다는 말 자체에 오류가 있었다.
사람들이 듣기에는 epoch마다 데이터셋이 변경되는 것인지 아니면 계속 새로운 데이터로 학습을 진행하는 건지 소통의 오류가 생길 수 도 있다고 하셨다.
그래서 다시 말을 고쳐본 것은 동일한 데이터셋을 가지고 학습을 진행해야 model이 정확하게 학습하는 지 아니면 랜덤 데이터 셋으로 학습을 진행해서 model이 정확히 예측하는지 어떻게 판단하는 질문이였고
내가 이해한 답변은 동일한 데이터셋으로 학습을 진행해야하며 계속 새로운 데이터로 새로 학습을 하게 된다면 loss, accuracy는 당연히 변할 수 밖에 없는 것이였다.
그리고 shuffle이라는 파라미터를 주의해야하는 것은 모델이 학습을 할 때 순서로도 학습을 할 수 있기 때문에 그걸 피하기 위해서는 간간히 shuffle을 쓰긴한다는 것이다.
이걸 토대로 데이터가 어떻게 들어가는지 한번 print로 찍어보자
"""
class DebugCallback(tf.keras.callbacks.Callback):
    def on_epoch_begin(self, epoch, logs=None):
        print(f"\n===== Epoch {epoch+1} 시작 =====")

    def on_train_batch_begin(self, batch, logs=None):
        print(f"  Batch {batch+1} 시작")

    def on_train_batch_end(self, batch, logs=None):
        print(f"  Batch {batch+1} 끝 - loss: {logs['loss']:.4f}, accuracy: {logs['accuracy']:.4f}")

    def on_epoch_end(self, epoch, logs=None):
        print(f"===== Epoch {epoch+1} 끝 - val_loss: {logs['val_loss']:.4f}, val_accuracy: {logs['val_accuracy']:.4f} =====")


# 412번과 동일한 모델 구조로 새로 생성
vgg_second = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
vgg_second.trainable = False

vgg_second_model = Sequential()
vgg_second_model.add(vgg_second)
vgg_second_model.add(GlobalAveragePooling2D())
vgg_second_model.add(Dense(256, activation='relu'))
vgg_second_model.add(Dense(num_classes, activation='softmax'))

optimizer = Adam(learning_rate=0.001)
loss_fn = tf.keras.losses.CategoricalCrossentropy()

vgg_second_model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

epochs = 10
for epoch in range(epochs):
    print(f"\n===== Epoch {epoch+1}/{epochs} =====")

    for batch_idx, (batch_x, batch_y) in enumerate(vgg_train):
        # 너무 많이 프린트되니까 몇개만 보자
        if batch_idx < 10 and epoch == 0:
          # ---- 입력 데이터 ----
          print(f"\n[배치 {batch_idx+1}]")
          print(f"  입력 x shape: {batch_x.shape}")        # (32, 224, 224, 3)
          print(f"  정답 y shape: {batch_y.shape}")        # (32, num_classes)
          print(f"  정답 y 예시: {batch_y[0].numpy()}")    # [0. 1. 0.] 같은 원-핫 벡터

        # ---- 순전파 + 역전파 ----
        with tf.GradientTape() as tape:
            predictions = vgg_second_model(batch_x, training=True)  # ---- 출력 데이터 ----
            loss = loss_fn(batch_y, predictions)

        if batch_idx < 10 and epoch == 0:
          print(f"  모델 출력(예측) shape: {predictions.shape}")   # (32, num_classes)
          print(f"  예측값 예시: {predictions[0].numpy()}")         # [0.2, 0.5, 0.3] 같은 확률
          print(f"  loss: {loss.numpy():.4f}")

        # ---- 가중치 업데이트 ----
        gradients = tape.gradient(loss, vgg_second_model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, vgg_second_model.trainable_variables))


loss, accuracy = vgg_second_model.evaluate(vgg_test)
print("--- VGG16 Second Model Test ---")
print(f"Test loss: {loss}")
print(f"Test accuracy: {accuracy}")
print()

"""
--- VGG16 Second Model Test ---
Test loss: 0.7173863649368286
Test accuracy: 0.71517413854599

[배치 1]
  입력 x shape: (32, 224, 224, 3)
  정답 y shape: (32, 3)
  정답 y 예시: [1. 0. 0.]
  모델 출력(예측) shape: (32, 3)
  예측값 예시: [0.4631366  0.36921385 0.16764961]
  loss: 0.6283

입력에서는 32개의 이미지로 이루어진 데이터가 들어가고 각 이미지가 224 높이와 넓이를 가지며 RGB로 이루어진 3채널로 들어온다.
x-shape = [
  이미지1: (224, 224, 3),
  이미지2: (224, 224, 3),
  이미지3: (224, 224, 3),
  ...,
  이미지32: (224, 224, 3)
]

정답의 y shape는 32개의 이미지로 이루어진 데이터에 3개의 클래스가 들어간다.
y-shape = [
  이미지1: [1, 0, 0],
  이미지2: [0, 1, 0],
  이미지3: [1, 0, 0],
  ...,
  이미지32: [0, 0, 1]
]

거기서 예측값이 (32, 3)으로 들어가고 y-shape처럼 들어갈 것이다.
그럼 예측값 예시를 보면 0번째 값이 0.46이므로 제일 높아서 이걸 정답으로 유추하고 맞추면 accuracy 중 맞춘 데이터값은 1점 올라간다.
그래서 (맞춘 수 / 전체 값) 하면 0.715로 높은 편이다.

Keras의 categorical_crossenthrophy는 log가 아닌 ln으로 계산한다.
따라서 loss율은 -ln(0.4631366) ~= 0.76973

이걸 동일하게 적용해보면
샘플 A: 예측 [0.9, 0.05, 0.05], 정답 [1,0,0]
→ accuracy: 맞음(1) / loss: -ln(0.9) = 0.10  (확신하며 맞음)

샘플 B: 예측 [0.4, 0.35, 0.25], 정답 [1,0,0]
→ accuracy: 맞음(1) / loss: -ln(0.4) = 0.92  (애매하게 맞음)

샘플 C: 예측 [0.3, 0.4, 0.3], 정답 [1,0,0]
→ accuracy: 틀림(0) / loss: -ln(0.3) = 1.20  (틀림)

이런식으로 계산해서 나온값이 0.717 인것이다.
0.717이기 때문에 그렇게 좋은 편은 아니라고 생각한다.
"""

###############################
#         GridSearch          #
###############################

# Define paths to the dataset
base_dir = 'rock_paper_scissors/'
train_dir = os.path.join(base_dir, 'train')
val_dir = os.path.join(base_dir, 'val')

# Image parameters
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32

# 하이퍼파라미터 기법을 사용하기 위해서 우선 Gridsearch라는걸 사용해보자
# 동일하게 위의 가위바위보 셋을 한번 사용해보자

# Load training data
grid_train = image_dataset_from_directory(
    train_dir,
    labels='inferred',
    label_mode='int',
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    interpolation='nearest',
    batch_size=None,
    shuffle=False,
    seed=SEED
)

def dataset_to_numpy(dataset):
    data = [(x.numpy(), y.numpy()) for x, y in dataset]
    X, y = zip(*data)
    return np.array(X), np.array(y)

X, y = dataset_to_numpy(grid_train)
X, y = shuffle(X, y)

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("--- Grid Search ---")
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print()



def create_model(learning_rate=0.001):
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    opt = Adam(learning_rate=learning_rate)

    model.compile(optimizer=opt, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# RAM 부족 관계로 기존 [0.001, 0.01, 0.1] 에서 [0.001, 0.01] 만 한다.
# learning_rates = [0.001, 0.01, 0.1]
# batch_sizes = [16, 32, 64]
learning_rates = [0.001, 0.01]
batch_sizes = [16, 32]
epochs = 10

best_accuracy = 0
best_params = {}

# 하이퍼파라미터 조합을 수동으로 설정하여 모델 학습 및 평가
num_classes = 3
input_shape = (224, 224, 3)

for lr in learning_rates:
    for batch_size in batch_sizes:
        model = create_model(learning_rate=lr)
        model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)

        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
        print(f"Learning Rate: {lr}, Batch Size: {batch_size}, Test Accuracy: {accuracy}")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_params = {'learning_rate': lr, 'batch_size': batch_size}

print("Best Parameters:", best_params)
print("Best Test Accuracy:", best_accuracy)
print()

"""
Learning Rate: 0.001, Batch Size: 16, Test Accuracy: 0.38235294818878174
Learning Rate: 0.001, Batch Size: 32, Test Accuracy: 0.38235294818878174
Learning Rate: 0.01, Batch Size: 16, Test Accuracy: 0.38235294818878174
Learning Rate: 0.01, Batch Size: 32, Test Accuracy: 0.38235294818878174

--- Grid Search ---
Best Parameters: {'learning_rate': 0.001, 'batch_size': 16}
Best Test Accuracy: 0.38235294818878174

colab에서 다른거 다 안돌리고 이것만돌려도 12.7GB를 다 잡아먹어서 learning rate를 줄이거나 배치 사이즈를 줄이거나 에포크를 줄여야했다.
그래서 우선 learning_rate를 줄여본 결과가 이거다.
우선 0.001과 배치사이즈가 16이 best인 이유는 0.001과 32와 정확도가 같다하더라도 비교식에서 최고점수를 비교하기때문에 이미 best에 들어간
16이 우선순위가 된다.

맥북에서 환경을 만들어서 테스트 돌려본 결과, 0.001이 제일 좋게나왔다. 여기서는 위와 다르게 결과가 좋았다.
Learning Rate: 0.001, Batch Size: 16, Test Accuracy: 0.8970588445663452
Learning Rate: 0.01, Batch Size: 16, Test Accuracy: 0.3529411852359772
Learning Rate: 0.1, Batch Size: 16, Test Accuracy: 0.37745097279548645
--- Grid Search ---
Best Parameters: {'learning_rate': 0.001, 'batch_size': 16}
Best Test Accuracy: 0.8970588445663452
"""

# 최적의 하이퍼파라미터로 모델 재학습
epochs = 10
best_model = create_model(learning_rate=best_params['learning_rate'])
best_model.fit(x_train, y_train, epochs=epochs, batch_size=best_params['batch_size'], validation_split=0.2)

# 테스트 데이터셋으로 모델 평가
test_loss, test_accuracy = best_model.evaluate(x_test, y_test)
print(f"Test Accuracy: {test_accuracy:.2f}")
print(f"Test Loss: {test_loss:.2f}")
print()

"""
Test Accuracy: 0.38
Test Loss: nan

왜 nan이 나올까 확인해보자.
내가 예상하기로는 전에 적은데이터에서 Resnet을 사용할때 trainable을 사용안하면 전체 학습데이터가 초기화되고 다시 학습하기 때문에
별로 소용이 없다고 했었다. 그럼 AI에게 검증을 받아보자.
"
ResNet50 안에는 BatchNormalization 레이어가 있어요. trainable=True인 상태로 큰 학습률(특히 lr=0.01)로 학습하면:

BatchNorm 파라미터(scale, shift) 업데이트
→ gradient가 너무 커서 분산(variance)이 0 또는 음수가 됨
→ 정규화 과정에서 0으로 나누기 발생
→ 가중치가 NaN으로 오염
→ 이후 모든 예측값이 NaN
→ loss = NaN
"
아 학습률이 높은게 문제가 되서 가중치가 오염되는 것을 알 수 있었다. 그럼 이를 타개하려면 어떤 방법이 있을까?
Trainable을 추가해서 막을 수도 있고 그렇게 한다 하더라도 데이터가 현저히 적어서 Dense(256)으로 변경하거나 Dropout을 고려하는게 좋다고 한다.
"""

###############################
#         RandomSearch        #
###############################

# Define paths to the dataset
base_dir = 'rock_paper_scissors/'
train_dir = os.path.join(base_dir, 'train')
val_dir = os.path.join(base_dir, 'val')

# Image parameters
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32

# 하이퍼파라미터 기법을 사용하기 위해서 우선 Gridsearch라는걸 사용해보자
# 동일하게 위의 가위바위보 셋을 한번 사용해보자

# Load training data
rnd_train = image_dataset_from_directory(
    train_dir,
    labels='inferred',
    label_mode='int',
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    interpolation='nearest',
    batch_size=None,
    shuffle=False,
    seed=SEED
)

def dataset_to_numpy(dataset):
    data = [(x.numpy(), y.numpy()) for x, y in dataset]
    X, y = zip(*data)
    return np.array(X), np.array(y)

X, y = dataset_to_numpy(rnd_train)
X, y = shuffle(X, y)

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print()
print("--- Grid Search ---")
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print()

def create_model(learning_rate=0.001):
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    base_model.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    opt = Adam(learning_rate=learning_rate)

    model.compile(optimizer=opt, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

num_classes = 3
input_shape = (224, 224, 3)

# 하이퍼파라미터 분포 정의
param_dist = {
    'learning_rate': uniform(0.001, 0.1),
    'batch_size': [16, 32, 64]
}

best_accuracy = 0
best_params = {}
n_iter = 5

# 랜덤하게 하이퍼파라미터 조합을 선택하여 시도
for params in ParameterSampler(param_dist, n_iter=n_iter, random_state=42):
    model = create_model(learning_rate=params['learning_rate'])
    model.fit(x_train, y_train, epochs=10, batch_size=params['batch_size'], validation_split=0.2, verbose=0)

    loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
    print(f"Params: {params}, Test Accuracy: {accuracy}")

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_params = params

print("Best Parameters (RandomSearch):", best_params)
print("Best Test Accuracy (RandomSearch):", best_accuracy)
print()

"""
Params: {'batch_size': 64, 'learning_rate': np.float64(0.08065429868602329)}, Test Accuracy: 0.28921568393707275
Params: {'batch_size': 64, 'learning_rate': np.float64(0.07419939418114051)}, Test Accuracy: 0.3382352888584137
Params: {'batch_size': 16, 'learning_rate': np.float64(0.0606850157946487)}, Test Accuracy: 0.36274510622024536
Params: {'batch_size': 32, 'learning_rate': np.float64(0.016599452033620267)}, Test Accuracy: 0.3382352888584137
Params: {'batch_size': 64, 'learning_rate': np.float64(0.04692488919658672)}, Test Accuracy: 0.28921568393707275
Best Parameters (RandomSearch): {'batch_size': 16, 'learning_rate': np.float64(0.0606850157946487)}
Best Test Accuracy (RandomSearch): 0.36274510622024536

음 여기서 오히려 정확도가 낮은게 보인다
여기도 동일하게 오염이 되지않았을까 싶은데
base_model.trainable = False
를 추가해서 한번 돌려보긴 해야겠다.

Params: {'batch_size': 64, 'learning_rate': np.float64(0.08065429868602329)}, Test Accuracy: 0.9509803652763367
Params: {'batch_size': 64, 'learning_rate': np.float64(0.07419939418114051)}, Test Accuracy: 0.6519607901573181
Params: {'batch_size': 16, 'learning_rate': np.float64(0.0606850157946487)}, Test Accuracy: 0.9558823704719543
Params: {'batch_size': 32, 'learning_rate': np.float64(0.016599452033620267)}, Test Accuracy: 0.9509803652763367
Params: {'batch_size': 64, 'learning_rate': np.float64(0.04692488919658672)}, Test Accuracy: 0.9656862616539001
Best Parameters (RandomSearch): {'batch_size': 64, 'learning_rate': np.float64(0.04692488919658672)}
Best Test Accuracy (RandomSearch): 0.9656862616539001

확실히 위와 다른 정확도를 보여주고 배치사이즈와 lr이 다른것을 확인할 수 있다.
"""

# 최적의 하이퍼파라미터로 모델 재학습
best_model = create_model(learning_rate=best_params['learning_rate'])
best_model.fit(x_train, y_train, epochs=10, batch_size=best_params['batch_size'], validation_split=0.2)

# 테스트 데이터셋으로 모델 평가
test_loss, test_accuracy = best_model.evaluate(x_test, y_test)
print(f"Test Accuracy: {test_accuracy:.2f}")
print(f"Test Loss: {test_loss:.2f}")
print()

"""
Trainable = True
Test Accuracy: 0.33
Test Loss: 2.69

Trainable = False
Test Accuracy: 0.90
Test Loss: 0.32
"""