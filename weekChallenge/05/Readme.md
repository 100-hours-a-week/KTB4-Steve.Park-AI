# Week 05 - CNN 전이학습(ResNet/VGG) & 한국어 Mini-GPT 챗봇

> KTB 위클리 챌린지 5주차 — ResNet50/VGG16 전이학습 비교 실험과, BPE 토크나이저부터 직접 구현한 한국어 Mini-GPT 챗봇

---

## 프로젝트 구조

```
05/
├── resnetvgg.py            # ResNet50 / VGG16 전이학습 비교 실험
└── chatbot/
    ├── basicdata/
    │   ├── mini_gpt.py      # 참고용 영문 Mini-GPT 베이스 구현
    │   ├── plan.md          # 프로젝트 계획 및 진행 기록 (Phase 0~6)
    │   └── 인공지능(CNN/NLP).pdf  # 참고 강의자료
    └── source/
        ├── app/
        │   └── app.py        # FastAPI 서빙 (앱소스)
        └── model/            # 토크나이저/아키텍처/학습 (모델소스)
            ├── bpe.py          # BPE 토크나이저 직접 구현
            ├── tokenizer.py    # 코퍼스 로딩 (kowikitext, 챗봇 Q&A)
            ├── model.py        # SOP_GPT (nanoGPT 스타일) 아키텍처
            ├── train_utils.py  # 공유 학습 루프 (early stopping)
            ├── main.py         # 진입점: train / chat / train_qa / chat_qa
            ├── chat.py         # CLI REPL 구현 (chat / chat_qa)
            ├── bpe_vocab.json  # 학습된 BPE vocab/merges
            ├── SOP_GPT.pt      # Stage 1 체크포인트
            └── SOP_GPT_qa.pt   # Stage 2 체크포인트
```

---

## 1. ResNet50 / VGG16 전이학습 (`resnetvgg.py`)

### 목표

전이학습(Transfer Learning)에서 **사전학습 가중치(`weights='imagenet'`)** 와 **`trainable` 설정**이 작은 데이터셋 학습에 어떤 영향을 주는지 ResNet50과 VGG16으로 비교 실험한다.

### 실험 A — 고양이/강아지 이진분류 (각 100장, thecatapi/thedogapi)

| 모델 | weights | trainable | Test Loss | Test Accuracy |
|------|---------|-----------|-----------|----------------|
| ResNet50 | `None` | True | 2.306 | 0.50 |
| ResNet50 | `imagenet` | True | 1.097 | 0.50 |
| ResNet50 | `imagenet` | **False** | **0.562** | **0.75** |
| VGG16 | `None` | True | 1.573 | 0.25 |
| VGG16 | `imagenet` | False (10 epoch) | 0.198 | 0.75 |
| VGG16 | `imagenet` | False (30 epoch) | **0.053** | **1.00** |
| VGG16 | `imagenet` | False (10 epoch, Dense(64)+Dropout(0.5)) | 0.053 | 1.00 |

> 매 실행마다 이미지를 API에서 새로 랜덤하게 받아오기 때문에 수치는 실행마다 달라질 수 있음 (재현을 위해선 동일 이미지셋 고정 필요).

### 실험 B — Rock-Paper-Scissors (3-class, 데이터셋 고정: `shuffle=False`, `seed=42`)

| 모델 | weights | trainable | Test Loss | Test Accuracy |
|------|---------|-----------|-----------|----------------|
| ResNet50 | `imagenet` | False | 0.803 | 0.682 |
| VGG16 | `imagenet` | False | 0.722 | 0.680 |
| VGG16 (수동 train loop, `GradientTape`) | `imagenet` | False | 0.717 | 0.715 |

### 실험 C — GridSearch (ResNet50, `trainable=True`)

`learning_rate ∈ {0.001, 0.01}` × `batch_size ∈ {16, 32}`

| 환경 | Best Params | Best Accuracy |
|------|-------------|----------------|
| Colab (메모리 12.7GB 한계) | lr=0.001, batch=16 | 0.382 |
| 로컬(맥북) | lr=0.001, batch=16 | **0.897** |

최적 파라미터로 재학습 → **Test Accuracy 0.38 / Test Loss `NaN`**
(원인: `trainable=True` + 높은 lr에서 ResNet50 내부 BatchNormalization의 분산이 0/음수가 되며 가중치가 NaN으로 오염)

### 실험 D — RandomSearch (ResNet50)

`learning_rate ~ Uniform(0.001, 0.1)`, `batch_size ∈ {16, 32, 64}`, `n_iter=5`

| trainable | Best Params | Best Accuracy |
|-----------|-------------|----------------|
| True | batch=16, lr≈0.0607 | 0.363 |
| **False** | batch=64, lr≈0.0469 | **0.966** |

최적 파라미터로 재학습 비교:

| trainable | Test Accuracy | Test Loss |
|-----------|---------------|-----------|
| True | 0.33 | 2.69 |
| **False** | **0.90** | **0.32** |

### 실행 방법

```bash
pip install tensorflow scikit-learn scipy pillow requests

# Rock-Paper-Scissors 데이터셋 (Kaggle)
kaggle datasets download glushko/rock-paper-scissors-dataset
unzip -q -o rock-paper-scissors-dataset.zip -d rock_paper_scissors

python resnetvgg.py
```

---

## 2. 한국어 Mini-GPT 챗봇 (`chatbot/`)

### 목표

- **Stage 1 (이어쓰기)**: 입력 문장을 autoregressive하게 이어써서 완전한 문장으로 끝맺는 모델
- **Stage 2 (Q&A)**: 질문에 대해 한 줄짜리 완결된 답변을 생성하는 모델
- 토크나이저는 BPE를 직접 구현, 최종적으로 FastAPI로 서빙

### 데이터

| 용도 | 데이터셋 | 크기 |
|------|---------|------|
| Stage 1 코퍼스 | kowikitext(dev+test 전체 + train 앞부분) + 챗봇 Q&A | 88.58M자 |
| Stage 2 코퍼스 | [songys/Chatbot_data](https://github.com/songys/Chatbot_data) Q&A 11,823쌍 | 459,846자 |

### BPE 토크나이저 직접 구현 (`bpe.py`)

- NFD로 자모 분해 후 BPE merge 학습, 출력 시 NFC로 재조합
- **base alphabet = 빈도 상위 300자 + UNK(U+FFFD)**, vocab_size=8000 (base 301 + merge 7699)
- 압축률(글자/토큰) 약 1.5x, encode→decode roundtrip 검증 완료

> 처음엔 코퍼스의 "고유 문자 전체(9188개)"를 base alphabet으로 써서 BPE_VOCAB_SIZE(8000)보다 커지는 바람에 merge가 단 한 번도 일어나지 않는 버그가 있었음 — base alphabet을 빈도 상위 300자로 제한하고 나머지를 UNK로 묶어 해결.

### 모델 아키텍처 (`model.py` — SOP_GPT, nanoGPT 스타일)

| 항목 | 값 |
|------|-----|
| block_size | 128 |
| n_embd | 256 |
| n_head | 4 |
| n_layer | 6 |
| batch_size | 64 |
| dropout | 0.2 |

### Stage 1 — 이어쓰기 (`main.py train` / `main.py chat`)

- 88.58M자 → 58.9M 토큰, **early stopping(patience=10)** 으로 val loss **3.514** (perplexity ~33.6)에서 종료
- 생성: `.`/`?`/`!`로 끝나는 토큰이 나오면 멈춤 + `temperature=0.8`, `top_k=40`, `repetition_penalty=1.3`
- 예) `안녕하` → `안녕하세요!`

### Stage 2 — Q&A fine-tuning (`main.py train_qa` / `main.py chat_qa`)

- `"질문: {q}\n답변: {a}\n\n"` 포맷, Stage 1과 동일한 BPE vocab 재사용
- Stage 1 가중치(`SOP_GPT.pt`)에서 이어서 fine-tuning (lr 1e-3 → 3e-4), 1100 step에서 early stop → val loss **3.738 → 2.185** (perplexity ~8.9)
- 생성: "\n"으로 끝나는 토큰이 나오면 한 줄("답변: ...")이 끝난 것으로 보고 멈춤

| 질문 | 답변 |
|------|------|
| 오늘 기분 어때? | 잘할 수 있을 거예요. |
| 취업 준비 잘하고 있어? | 열심히 하세요. |
| 사랑해 | 사랑은 소유하는게 아니라죠. |

### FastAPI 서빙 (`app/app.py`)

| 엔드포인트 | 설명 |
|-----------|------|
| `POST /generate` | Stage 1 이어쓰기 (`.`/`?`/`!`에서 정지) |
| `POST /chat` | Stage 2 Q&A (줄바꿈에서 정지) |
| `GET /` | 테스트용 HTML 페이지 |
| `GET /docs` | Swagger UI |

### 실행 방법

```bash
pip install torch Korpora fastapi uvicorn

cd chatbot/source/model

# Stage 1 학습 (BPE 학습 + 88M자 코퍼스 인코딩 — 오래 걸림)
python main.py train
python main.py chat           # 이어쓰기 REPL

# Stage 2 fine-tuning (Stage 1 가중치에서 이어서 학습)
python main.py train_qa
python main.py chat_qa        # Q&A REPL

# FastAPI 서빙
cd ../app
uvicorn app:app --reload      # http://127.0.0.1:8000  (/docs 에서 Swagger UI)
```

> `model/` 안의 스크립트는 그 디렉터리에서 실행해야 `bpe_vocab.json`/체크포인트 상대경로가 맞음. `app/app.py`는 `__file__` 기준으로 `../model`을 참조하므로 어디서 실행해도 동작함.

---

## 사용 라이브러리

- `tensorflow` / `keras` — ResNet50, VGG16, GridSearch/RandomSearch 실험
- `scikit-learn`, `scipy` — train/test split, `ParameterSampler`, `uniform`
- `requests`, `Pillow` — 이미지 API 다운로드/전처리
- `torch` — Mini-GPT 모델 구현 및 학습 (MPS)
- `Korpora` — kowikitext 코퍼스
- `fastapi`, `uvicorn`, `pydantic` — 챗봇 서빙

---

## 회고

### 한국어 챗봇

<details>
<summary><b>1. BPE merge가 단 한 번도 일어나지 않는 버그</b></summary>

BPE와 모델 구조를 다 갖추고 첫 학습을 돌렸는데, vocab_size가 코퍼스의 고유 문자 수(9188)와 정확히 같게 나왔다. 그리고 모든 토큰의 길이가 1 — merge가 단 한 번도 일어나지 않은 것이다.

원인은 base alphabet을 "코퍼스에 등장하는 모든 문자"로 잡았던 것. 그 개수(9188)가 이미 목표 vocab_size(8000)보다 컸다. BPE는 "가장 자주 붙어다니는 pair를 merge해서 새 토큰을 만들고 vocab_size에 도달하면 멈춘다"는 알고리즘인데, 시작점부터 목표치를 넘어가 있으니 merge 루프 자체가 실행되지 못하고 그냥 자모 단위 토크나이저로 끝나버렸다.

해결은 **base alphabet을 빈도 상위 300자로 제한하고, 나머지 희귀 문자는 모두 UNK(U+FFFD) 하나로 묶는 것**이었다. base 301(300+UNK) + merge 7699 = 8000개로 merge가 일어날 공간이 생겼고, 압축률도 1.5x로 정상적으로 나왔으며 encode→decode roundtrip도 깨지지 않았다. "vocab_size를 늘리면 되지 않을까" 싶었지만 그건 문제를 미루는 것일 뿐 — 코퍼스에 한자/이모지 등이 조금만 늘어도 같은 문제가 재발할 구조였다. UNK 버킷팅이 근본적인 해결이었다.

</details>

<details>
<summary><b>2. 처음엔 말이 안 되는 문장만 나왔다 — 데이터량과 early stopping</b></summary>

BPE 버그를 고치고 처음 학습한 모델의 생성 결과는, 문장부호 없이 끝없이 이어지거나 위키 캐스트 목록("이름 - 역할 역, 이름 - 역할 역, ...")을 그대로 반복하며 200토큰을 다 채우는 식이었다. "이어쓰기"라는 목표와는 거리가 멀었다.

여기서 두 가지를 동시에 손봤다.

- **코퍼스를 10배(88.58M자)로 늘렸다** — kowikitext의 dev+test 전체 + train 앞부분 80M자 + 챗봇 데이터.
- **early stopping(patience=10, min_delta=1e-3)을 도입**해서, val loss가 더 안 떨어지는 시점에서 멈추고 그때의 best 가중치를 저장하도록 했다.

그 결과 val loss가 3.514(perplexity ~33.6)까지 내려가면서 "안녕하" → "안녕하세요!" 처럼 짧고 문법적으로 끝나는 문장이 나오기 시작했다. 데이터 양과 "적당한 시점에서 멈추는 것" 둘 다 중요하다는 걸 체감했다. 하지만 아직도 길게 적거나
"아니, 근데" 이런식으로 시작하면 위키 문서의 도입부가 나오거나 다른 문자들이 나온다. 이를 보완할 방법이 필요하다.

</details>

<details>
<summary><b>3. 그래도 가끔 같은 말을 반복했다 — repetition_penalty</b></summary>

early stopping 이후에도 가끔 같은 토큰/구절을 반복하면서 200토큰 한도를 다 채우는 경우가 있었다. `temperature`와 `top_k`만으로는 한 번 반복 루프에 들어간 걸 빠져나오기 어려웠다.

`repetition_penalty=1.3`을 추가해서, 직전 block_size(128) 토큰 안에 이미 등장한 토큰의 logit을 깎도록 했다. 양수 logit이면 penalty로 나누고 음수 logit이면 곱해서 더 작게 만든다 — "이미 한 번 말한 건 다시 말할 확률을 낮춘다"는 단순한 규칙인데, 이게 들어가니 반복 루프가 사라지고 거의 모든 출력이 `.`/`?`/`!`에서 자연스럽게 멈췄다.

</details>

<details>
<summary><b>4. Stage1 → Stage2, 어떻게 이어붙일까</b></summary>

"이어쓰기" 모델을 "질문에 답하는" 모델로 바꿀 때, 처음부터(zero) 새로 학습시킬지(A안) 아니면 Stage1 가중치에서 이어서 fine-tuning할지(B안) 고민했다.

데이터 양 차이가 컸다 — Stage1은 88M자인데 Stage2 Q&A 데이터는 46만자뿐이다. 이 작은 데이터로 처음부터 학습시키면 한국어 자체를 제대로 못 배운 채 "질문:/답변:" 패턴만 외울 가능성이 높다고 판단해서 **B안(Stage1 가중치에서 이어서 fine-tuning)**으로 갔다.

다만 Stage1과 같은 lr(1e-3)을 그대로 쓰면 몇 step만에 Stage1에서 배운 한국어 자체를 "잊어버릴" 수 있어서(catastrophic forgetting), lr을 3e-4로 낮췄다. 결과적으로 1100 step만에 val loss가 3.738 → 2.185로 떨어졌고, "취업 준비 잘하고 있어?" → "열심히 하세요." 같이 짧고 자연스러운 응답이 나왔다. 작은 모델/작은 데이터에서는 "처음부터 다시"보다 "이미 아는 걸 살짝 트는" 쪽이 훨씬 효율적이라는 걸 확인했다.

</details>

<details>
<summary><b>5. 디렉토리/진입점 정리 — app과 model, 그리고 main.py</b></summary>

처음엔 `train.py`(이어쓰기)와 `finetune_qa.py`(Q&A)가 따로 있었는데, 둘 다 모듈 최상단에서 자기 코퍼스를 로드/인코딩하는 구조였다. 문제는 `train.py`를 chat 모드로 실행해도 88M자 코퍼스를 매번 다시 인코딩한다는 것 — REPL 진입까지 2분 넘게 걸렸다.

FastAPI로 서빙하면서 `app/`(서빙)과 `model/`(토크나이저/아키텍처/학습/체크포인트)로 디렉토리를 나눴고, `app/app.py`는 `__file__` 기준으로 `../model`을 `sys.path`에 추가해 어디서 실행해도 동작하게 했다.

마지막으로 `train.py`/`finetune_qa.py`를 `main.py` 하나로 합치면서, **각 모드(`train`/`chat`/`train_qa`/`chat_qa`)가 실제로 필요한 데이터만 로드하도록** 정리했다 — `chat`/`chat_qa`/`train_qa`는 더 이상 88M자 Stage1 코퍼스를 만지지 않는다. 처음에 겪었던 "REPL 켜는데 2분"이 이 구조 정리로 자연스럽게 해결됐다.

</details>

### ResNet50 / VGG16 전이학습

<details>
<summary><b>1. weights=None인데 왜 loss가 2.3까지 나오지?</b></summary>

ResNet50을 `weights=None`으로 불러와 고양이/강아지 100장으로 학습시켰더니 loss 2.31, accuracy 0.5 — 거의 찍기 수준이었다. 처음엔 "100장이 너무 적어서 그런가" 정도로만 생각했는데, `weights=None`은 **완전히 랜덤 초기화된 가중치**라서 100장으로는 패턴을 배울 수 없다는 걸 알게 됐다.

그래서 `weights='imagenet'`으로 바꿔봤는데, `trainable`을 따로 설정하지 않으면(=기본값 True) 오히려 loss가 1.10으로 더 나빠졌다 — **사전학습된 가중치를 100장짜리 데이터로 덮어쓰면서 오염**되기 때문이었다. 여기에 `trainable=False`를 추가하자(ResNet 레이어는 동결하고 Dense 레이어만 학습) loss 0.56/accuracy 0.75로 확실히 좋아졌다.

정리하면: `weights=None`은 데이터가 적으면 아무것도 못 배우고, `weights='imagenet'`이라도 `trainable=True`면 적은 데이터가 사전학습 가중치를 오염시킨다. **작은 데이터셋 + 사전학습 가중치 + `trainable=False`(freeze)** 조합이 핵심이라는 걸 여기서 처음 체감했다.

</details>

<details>
<summary><b>2. VGG16은 거의 0.25(찍기) — gradient vanishing</b></summary>

같은 100장으로 VGG16(`weights=None`)을 돌렸더니 accuracy 0.25, loss 1.57 — ResNet보다도 더 안 나왔다. "ResNet은 잘못된 학습이라도 했는데 VGG16은 거의 학습을 못 한 것"이라는 결론에 도달했다.

이유는 **gradient vanishing**이었다. VGG16은 ResNet과 달리 skip connection이 없어서, 레이어를 통과할수록 gradient가 계속 곱해지며 작아진다. 활성화 함수의 도함수가 평균 0.9 정도라고 치면 16개 레이어를 통과하면 0.9^16 ≈ 0.185 — 출력층에 도달하는 gradient가 거의 사라진다는 계산이다.

VGG16도 `weights='imagenet'` + `trainable=False`로 바꾸자 loss 0.198/accuracy 0.75(10 epoch), epoch을 30으로 늘리니 loss 0.053/accuracy 1.0까지 나왔다. "사전학습 가중치를 그대로 쓰고 마지막 분류기만 학습"하는 게 처음부터 끝까지 직접 학습시키는 것보다 훨씬 안정적이라는 걸 ResNet/VGG 둘 다에서 확인했다.

</details>

<details>
<summary><b>3. "어? 다시 돌렸는데 결과가 또 똑같이 나오네" — 랜덤 이미지의 함정</b></summary>

VGG16에 Dense(64)+Dropout(0.5)을 추가해서 다시 돌렸는데, 바로 위(epoch=30) 결과와 loss/accuracy가 토씨 하나 안 틀리고 똑같이 나왔다(0.053/1.0). 처음엔 "오 정확하네" 싶었는데, 뒤늦게 떠올린 게 있다 — **이 코드는 매번 thecatapi/thedogapi에서 이미지를 새로 랜덤하게 받아온다.** 즉 매 실행마다 학습/테스트 데이터 자체가 달라지는데, 수치가 고정될 이유가 없었다.

이걸 깨닫고 "재현 가능한 비교를 하려면 데이터셋을 고정해야 한다"는 결론에 도달했고, 다음 실험(ResNet vs VGG16)부터는 Kaggle의 고정된 Rock-Paper-Scissors 데이터셋을 `shuffle=False`, `seed=42`로 불러왔다.

</details>

<details>
<summary><b>4. ResNet vs VGG16, "모델 캘리브레이션"</b></summary>

가위바위보 데이터셋(고정)으로 ResNet50과 VGG16을 동일 조건(`imagenet`, `trainable=False`, lr=0.001, 10 epoch)에서 비교했더니, accuracy는 ResNet 0.682 / VGG16 0.680로 거의 같은데 **loss는 ResNet(0.803)이 VGG16(0.722)보다 더 높았다.** accuracy가 비슷한데 loss가 다르다는 게 처음엔 이해가 안 됐다.

찾아보니 "모델 캘리브레이션" 차이였다 — **ResNet은 확신을 갖고 예측하다가 틀리면 loss가 크게 뛰고, VGG16은 애매하게 예측해서 맞든 틀리든 loss 변화가 작다.** 같은 정확도라도 "얼마나 확신을 갖고 맞히고 틀리는지"에 따라 loss가 달라진다는 것.

이 과정에서 강사님(Alex)에게 "데이터셋을 고정한다"는 표현에 대해서도 피드백을 받았다. "고정"이라고만 하면 epoch마다 데이터가 바뀌는지/안 바뀌는지 듣는 사람마다 다르게 해석할 수 있다는 것. 정확히는 "동일한 데이터셋으로 학습해야 모델 성능을 정확히 비교할 수 있다"는 의미였고, `shuffle` 파라미터도 — 모델이 데이터 순서 자체를 외워버릴 수 있어서 종종 의도적으로 켜준다는 점을 함께 짚어주셨다. 용어를 정확히 쓰는 것의 중요성을 느꼈다.

</details>

<details>
<summary><b>5. categorical_crossentropy를 손으로 계산해보기</b></summary>

`-ln(p)` 식으로 loss를 계산한다는 건 알고 있었지만, 실제 batch가 들어가서 loss로 나오는 과정을 직접 본 적은 없었다. 그래서 `tf.GradientTape`로 수동 학습 루프를 짜고, `DebugCallback`/print로 첫 10개 배치의 입력 shape, 정답 원-핫 벡터, 모델 예측값, loss를 그대로 찍어봤다.

예를 들어 정답이 `[1,0,0]`이고 예측이 `[0.4631, 0.3692, 0.1676]`이면, 가장 큰 값(0.4631)이 0번 클래스라서 accuracy는 맞은 걸로 카운트되고, loss는 `-ln(0.4631) ≈ 0.7697`. 몇 가지 케이스로 정리해보면:

- 예측 `[0.9, 0.05, 0.05]`, 정답 `[1,0,0]` → 맞음, loss `-ln(0.9)=0.10` (확신하며 맞음)
- 예측 `[0.4, 0.35, 0.25]`, 정답 `[1,0,0]` → 맞음, loss `-ln(0.4)=0.92` (애매하게 맞음)
- 예측 `[0.3, 0.4, 0.3]`, 정답 `[1,0,0]` → 틀림, loss `-ln(0.3)=1.20`

"accuracy는 1등만 보지만 loss는 확신의 정도까지 본다"는 게 숫자로 보이니 훨씬 명확해졌다. 이 수동 루프의 최종 결과(loss 0.717/accuracy 0.715)도 "확신의 정도"라는 관점에서 보면 그렇게 나쁘지 않은 수치라고 판단했다.

</details>

<details>
<summary><b>6. GridSearch — Colab 메모리 한계, 그리고 NaN</b></summary>

`learning_rate × batch_size` 조합을 GridSearch로 돌리려고 했는데, Colab에서 원래 계획한 `[0.001, 0.01, 0.1] × [16, 32, 64]`(9가지 조합)을 돌리자 그것만으로 12.7GB 메모리를 다 잡아먹었다. 결국 `[0.001, 0.01] × [16, 32]`(4가지)로 줄였는데, **Colab에서는 4개 조합 모두 정확히 0.382로 동일한 결과**가 나왔다 — 사실상 학습이 안 되고 있다는 신호였다.

같은 코드를 맥북에서 돌리니 `lr=0.001, batch=16`이 0.897로 가장 좋았고 `lr=0.01`, `lr=0.1`은 0.35 안팎이었다. 환경(Colab vs 로컬)에 따라 결과가 이렇게 달라질 수 있다는 게 흥미로웠다.

여기서 끝이 아니었다 — best 파라미터(`lr=0.001, batch=16`)로 재학습했더니 **Test Loss가 `nan`**으로 나왔다. 원인을 찾아보니, 이 GridSearch의 `create_model`은 `base_model.trainable`을 설정하지 않아 기본값 True였고, ResNet50 내부의 BatchNormalization이 `trainable=True` + 상대적으로 큰 학습률 조합에서 분산이 0/음수가 되어 0으로 나누기가 발생 → 가중치가 NaN으로 오염 → 이후 모든 예측이 NaN이 되는 구조였다. "전이학습에서 trainable을 안 정해주면 또 이 문제가 나오는구나"를 다시 한 번 절감했다.

</details>

<details>
<summary><b>7. RandomSearch — trainable 하나 빠뜨려서 결과가 전부 낮게 나왔다</b></summary>

RandomSearch도 처음엔 GridSearch와 같은 `create_model`을 그대로 썼는데(=`trainable` 미설정), 5개 조합 모두 accuracy가 0.28~0.36 사이로 거의 비슷하게 낮았다. "이것도 GridSearch처럼 가중치가 오염된 거 아닐까" 싶어서 `create_model`에 `base_model.trainable = False`를 추가하고 다시 돌렸다.

결과는 확실히 달랐다 — 같은 `param_dist`(`learning_rate ~ Uniform(0.001, 0.1)`, `batch_size ∈ {16,32,64}`)인데도 accuracy가 0.65~0.97 범위로 올라갔고, best 조합(`batch=64, lr≈0.0469`)으로 재학습했을 때 Trainable=True는 Test Accuracy 0.33/Loss 2.69, Trainable=False는 Test Accuracy 0.90/Loss 0.32로 큰 차이가 났다.

결국 이번 주 ResNet/VGG16 실험 전체를 관통하는 결론은 하나였다 — **작은 데이터셋으로 전이학습을 할 때는 `base_model.trainable = False`를 빠뜨리지 않는 것**이 가장 중요했고, 이걸 까먹을 때마다 loss가 치솟거나 NaN이 나오는 식으로 매번 다시 확인하게 됐다.

</details>
