import requests

# 라즈베리파이의 IP 주소와 포트 번호
raspberry_pi_ip = "10.0.0.2"
raspberry_pi_port = 5000

# POST 요청을 보낼 URL
url = f"http://{raspberry_pi_ip}:{raspberry_pi_port}/control_led"

# POST로 보낼 데이터 (LED를 켜려면 1, 끄려면 0)
data = {"led_value": 0}

# POST 요청 보내기
response = requests.post(url, json=data)
##
# 응답 출력
print(response.text)
