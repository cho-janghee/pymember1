# ai_digits_classifier.py  머신러닝 코드
# 머신러닝 기술이 적용된 부분:
# ① 모델 선택(LogisticRegression)
# ② 모델 학습(fit)
# ③ 모델 예측(predict)
# 실제 AI가 “배우는” 순간은 fit()에서 발생합니다.

import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# 1. 데이터셋 로드 (손글씨 숫자 데이터)
digits = datasets.load_digits()

print("데이터 구조:", digits.data.shape)  # (1797, 64) → 1797개의 샘플, 8x8 이미지 픽셀(64개)

# 2. 시각적으로 데이터 확인
plt.gray()
plt.matshow(digits.images[0])  # 첫 번째 이미지 보기
plt.title(f"Label: {digits.target[0]}")
plt.show()

# 3. 데이터셋 분리 (학습용 80%, 테스트용 20%)
X_train, X_test, y_train, y_test = train_test_split(
    digits.data, digits.target, test_size=0.2, random_state=42
)

# 4. 모델 생성 (로지스틱 회귀)
model = LogisticRegression(max_iter=1000)  # 반복 횟수 증가(수렴을 위해)
model.fit(X_train, y_train)  # 학습 시작

# 5. 예측
y_pred = model.predict(X_test)

# 6. 정확도 출력
print("정확도:", accuracy_score(y_test, y_pred))
print("\n분류 리포트:\n", classification_report(y_test, y_pred))

# 7. 테스트 데이터 몇 개 시각화
fig, axes = plt.subplots(2, 5, figsize=(8, 4))
for ax, image, label, pred in zip(axes.ravel(), X_test, y_test, y_pred):
    ax.imshow(image.reshape(8, 8), cmap=plt.cm.gray_r, interpolation='nearest')
    ax.set_title(f"T:{label} P:{pred}")
    ax.axis('off')
plt.tight_layout()
plt.show()
