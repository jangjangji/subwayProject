import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import random

plt.rcParams['font.family'] = 'Malgun Gothic'

# YOLOv4 모델과 관련된 파일 경로 설정
config_path = 'C:/py_opencv_object_detection/darknet/yolov4.cfg'
weight_path = 'C:/py_opencv_object_detection/darknet/yolov4.weights'
class_path = 'C:/py_opencv_object_detection/darknet/coco.names'

# 클래스 이름 로드
with open(class_path, 'r') as f:
    classes = f.read().splitlines()

# YOLOv4 모델 로드
net = cv2.dnn.readNetFromDarknet(config_path, weight_path)
result_list = []
result_list3 = []
result_list4 = []

# 이미지 파일 경로를 자동으로 읽어들이기l
image_dir = 'piimg'  # 이미지 파일이 있는 디렉토리 경로
image_paths = [os.path.join(image_dir, filename) for filename in os.listdir(image_dir) if filename.endswith(('.jpg', '.png', '.jpeg'))]
file_list = os.listdir(image_dir)

for image_path in image_paths:
    # 이미지를 불러와서 네트워크 입력 크기로 조정
    image = cv2.imread(image_path)
    # 이미지 주변의 검정색 여백 제거
    image = cv2.copyMakeBorder(image, 0, 0, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    # 이미지 샤프닝 처리
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened_image = cv2.filter2D(gray, -1, sharpening_kernel)
    sharpened_image_bgr = cv2.cvtColor(sharpened_image, cv2.COLOR_GRAY2BGR)
    image = sharpened_image_bgr

    height, width, _ = image.shape

    # 이미지의 가로와 세로 값을 곱한 값을 15m^2로 가정
    desired_area_meters = 15.0

    # 이미지의 가로와 세로 값을 곱한 값에 해당하는 비율 계산
    pixels_per_meter = np.sqrt((width * height) / desired_area_meters)
    image_height_meters = height / pixels_per_meter
    image_width_meters = width / pixels_per_meter

    # YOLOv4 모델을 통해 객체 감지
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_layers_names)

    # 객체 감지 후 사람 클래스 필터링
    conf_threshold = 0.1  # 객체 감지 임계값
    nms_threshold = 0.2  # 비최대 억제 임계값

    class_ids = []
    boxes = []
    confidences = []
    # 외각선 면적 필터링 임계값
    min_contour_area_threshold = 100  # 예: 100픽셀 이상의 면적을 가진 객체만 유지
    max_contour_area_threshold = 100000 

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > conf_threshold and class_id == 0:  # 사람 클래스 필터링
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)


                # 객체의 외각선 면적 계산
                contour_area = w * h

                if min_contour_area_threshold <= contour_area <= max_contour_area_threshold:
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

    # 비최대 억제 적용하여 겹치는 박스 제거
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # 객체의 외곽선 찾기
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 외곽선 그리기
    for i in range(len(boxes)):
        if i in indices:
            x, y, w, h = boxes[i]
            x_meters = (x / pixels_per_meter)
            y_meters = (y / pixels_per_meter)
            w_meters = (w / pixels_per_meter)
            h_meters = (h / pixels_per_meter)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f'{w_meters:.3f}m x {h_meters:.3f}m', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(image, f'Area: {w_meters * h_meters:.3f}m^2', (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 객체의 외곽선 면적 계산을 위한 리스트
    contour_areas = []
    n=0

    # 객체의 외곽선을 순회하며 면적 계산
    for contour in contours:
        area = cv2.contourArea(contour)
        # 이미지의 가로세로 비율로 면적을 변환하여 contour_areas에 추가
        adjusted_area = area / (pixels_per_meter ** 2)  # 이미지의 가로세로 비율로 변환
        contour_areas.append(adjusted_area)
        #print(f'{n}.Contour Area: {adjusted_area:.3f}m^2')
        n+=1

    # 객체의 외곽선 면적의 합 계산
    total_contour_area = sum(contour_areas)
    # 전체 이미지 면적 계산
    total_area = image_height_meters * image_width_meters

    # 객체를 제외한 영역의 면적 계산
    region_area = total_area - total_contour_area
    result_list.append(region_area)
    random.shuffle(result_list)

    result_list3 = result_list[:8]
    result_list4 = result_list[8:16]
    print(f'전체 이미지 면적 (객체의 외곽선 면적 포함): {image_height_meters:.3f}m * {image_width_meters:.3f}m')
    print(f'객체의 외곽선 면적의 합: {total_contour_area:.3f}m^2')
    print(f'남는 공간 면적 (객체의 외곽선 면적 제외): {region_area:.3f}m^2')

    


    # 결과 이미지 표시와 면적 정보 함께 출력
    fig, ax = plt.subplots()
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    ax.imshow(image_rgb)
    ax.axis('off')
    ax.set_title('객체 제외 영역')

    font_path = 'C:/Windows/Fonts/malgun.ttf'  # Malgun Gothic 폰트 경로
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 이미지에 텍스트 추가
    image_with_text = image.copy()

    cv2.putText(image_with_text, f'total: {image_height_meters:.3f}m * {image_width_meters:.3f}m', (10, height - 80), font, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image_with_text, f'contour: {total_contour_area:.3f}m^2', (10, height - 40), font, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image_with_text, f'outside: {region_area:.3f}m^2', (10, height - 10), font, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

    # 이미지 표시
    # 이미지 창 열기
    cv2.namedWindow('Image with Area Information', cv2.WINDOW_NORMAL)  # 창 크기 조절 가능한 모드
    cv2.imshow('Image with Area Information', image_with_text)
    cv2.resizeWindow('Image with Area Information', 800, 600)  # 창 크기 조절

    cv2.waitKey(1000)  # 아무 키나 누를 때까지 대기
    # 윈도우 창 닫기
    cv2.destroyAllWindows()

raspberry_pi_ip = "10.0.0.2"
raspberry_pi_port = 5000
url = f"http://{raspberry_pi_ip}:{raspberry_pi_port}/control_led"
      
data = {
    "region_area1": result_list3[0],
    "region_area2": result_list3[1],
    "region_area3": result_list3[2]
} 
response = requests.post(url, json=data)
        
    # 각 요청에 대한 응답 출력
print(f"region_area에 대한 응답: {response.text}")
print("result_list:", result_list)
print("result_list3:", result_list3)
print("result_list4:", result_list4)