# ai_digits_cnn_keras.py
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# 1. 데이터 로드 (scikit-learn digits: 8x8 회색 이미지, 라벨 0~9)
digits = datasets.load_digits()
X = digits.images            # shape: (1797, 8, 8)
y = digits.target            # shape: (1797,)

# 2. 전처리: 정규화 & CNN 입력 형태로 변환
# 픽셀 값 범위(0~16)를 0~1로 스케일링
X = X.astype("float32") / 16.0

# Keras CNN 입력은 (H, W, C) 채널 포함 필요 → (8, 8, 1)
X = np.expand_dims(X, axis=-1)  # (1797, 8, 8, 1)

# 3. 학습/테스트 분할 (라벨 분포 유지 위해 stratify 권장)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. 모델 구성 (아주 가벼운 CNN)
# 8x8이라 작은 편이라 과한 네트워크는 오히려 과적합/역효과 날 수 있음
model = keras.Sequential([
    layers.Input(shape=(8, 8, 1)),
    layers.Conv2D(16, (3, 3), padding="same", activation="relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(32, (3, 3), padding="same", activation="relu"),
    layers.Flatten(),
    layers.Dense(64, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(10, activation="softmax")
])

model.compile(
    optimizer=keras.optimizers.Adam(),
    loss="sparse_categorical_cross entropy",  # y가 정수라면 sparse_* 사용
    metrics=["accuracy"]
)

print(model.summary())

# 5. 학습(Validation split 사용) + 조기종료
early_stop = keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=5, restore_best_weights=True
)

history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=50,
    batch_size=32,
    callbacks=[early_stop],
    verbose=1
)

# 6. 테스트 평가
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\n[테스트 세트] loss={test_loss:.4f}, accuracy={test_acc:.4f}")

# 7. 분류 리포트 & 혼동행렬
y_prob = model.predict(X_test, verbose=0)
y_pred = np.argmax(y_prob, axis=1)

print("\n[Classification Report]")
print(classification_report(y_test, y_pred, digits=4))

print("[Confusion Matrix]")
print(confusion_matrix(y_test, y_pred))

# 8. 학습 곡선 시각화
plt.figure(figsize=(6,4))
plt.plot(history.history["loss"], label="train_loss")
plt.plot(history.history["val_loss"], label="val_loss")
plt.title("Training vs Validation Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(6,4))
plt.plot(history.history["accuracy"], label="train_acc")
plt.plot(history.history["val_accuracy"], label="val_acc")
plt.title("Training vs Validation Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.tight_layout()
plt.show()

# 9. 예측 결과 샘플 시각화 (10개)
n_show = 10
plt.figure(figsize=(10, 2))
for i in range(n_show):
    ax = plt.subplot(1, n_show, i + 1)
    img = X_test[i].squeeze()  # (8, 8)
    ax.imshow(img, cmap="gray", interpolation="nearest")
    ax.set_title(f"T:{y_test[i]}\nP:{y_pred[i]}")
    ax.axis("off")
plt.tight_layout()
plt.show()
