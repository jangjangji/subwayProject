import cv2
import numpy as np



# 입력 이미지 경로
image_path = 'piimg/2.jpg'

# 이미지 불러오기

img = cv2.imread(image_path)
image = cv2.resize(img,dsize=(500,500),interpolation=cv2.INTER_AREA)

def object_detection(image):

    # 이미지를 그레이스케일로 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 바이너리 이미지로 변환 (흰색: 바닥, 검은색: 객체)
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # 노이즈 제거를 위한 모폴로지 연산
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

    # 객체의 외곽선 찾기
    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 최소한의 사각형 또는 붙어있는 객체들의 외곽선을 그리기 위한 리스트
    bounding_boxes = []

    # 객체의 외곽선을 순회하며 최소한의 사각형 또는 붙어있는 객체들의 외곽선 그리기
    for contour in contours:
        # 객체의 면적 계산
        area = cv2.contourArea(contour)
        
        # 작은 객체 제거를 위한 조건 설정 (면적 기준 수정 가능)
        if area > 2000:
            # 객체의 외곽선 근사화
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # 외곽선 그리기
            cv2.drawContours(image, [approx], 0, (0, 255, 0), 2)
            
            # 객체에 외곽선이 그려진 최소한의 사각형 계산
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            
            # 사각형 그리기
            cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
            
            # 객체 영역을 감싸는 외곽선 그리기
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            # 최소한의 사각형 좌표를 bounding_boxes 리스트에 추가
            bounding_boxes.append(box)

    return image, contours


    # 외곽선이 그려진 이미지 출력
cv2.imshow('Contours', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
