import requests
import json

def send_data(image_height_meters,image_width_meters,total_contour_area,region_area):
    raspberry_pi_url = "http://10.0.0.2:8082/data_receive"
    data = {
        "width":image_width_meters,
        "height": image_height_meters,
        "total_contour_area": total_contour_area,
        "region_area": region_area
    }

    response = requests.post(raspberry_pi_url, json=data, headers={'Content-Type': 'application/json'})
###
    if response.status_code == 200:
        print("Data sent successfully")
    else:
        print("Failed to send data")
