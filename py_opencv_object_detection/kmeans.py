import cv2
import numpy as np
from sklearn.cluster import DBSCAN

# 이미지 읽기
image = cv2.imread('imgs/4line7.jpg', cv2.IMREAD_GRAYSCALE)

# 이진화: 이미지를 흑백으로 변환하고 임계값 적용
_, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)

# 윤곽선 찾기
contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 찾은 윤곽선을 타원으로 근사화
ellipses = []
for contour in contours:
    if len(contour) >= 5:
        ellipse = cv2.fitEllipse(contour)
        ellipses.append(ellipse)

# DBSCAN 클러스터링
ellipses = [ellipse[0] for ellipse in ellipses]  # 타원 중심만 사용

dbscan = DBSCAN(eps=20, min_samples=5)
labels = dbscan.fit_predict(ellipses)

# 클러스터 수와 레이블 출력
num_clusters = len(set(labels))
print(f"클러스터 수: {num_clusters}")

# 클러스터링 결과 시각화
output_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

for i in range(num_clusters):
    mask = labels == i
    color = np.random.randint(0, 256, size=3)
    for j, center in enumerate(np.array(ellipses)[mask]):
        center = (int(center[0]), int(center[1]))
        cv2.circle(output_image, center, 2, color, -1)

# 결과 이미지 표시
cv2.imshow('Clustering Result', output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
