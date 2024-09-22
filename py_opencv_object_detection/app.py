from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse, abort
from db import db_value_list, db_value_list3,db_value_list4  # db.py 모듈에서 db_value_list1을 가져옴

app = Flask(__name__)

@app.route('/get_db_values', methods=['GET'])
def get_db_values():
    # db_value_list1 값을 가져와서 사용
    # 각 항목을 딕셔너리로 변환
    data_list = [{'value': item} for item in db_value_list]
    data_list3 = [{'value3': item3} for item3 in db_value_list3]
    data_list4 = [{'value4': item4} for item4 in db_value_list4]

    # 데이터를 JSON으로 변환하고 반환
    response = jsonify({'db_values': data_list,
                        'db_values3': data_list3,
                        'db_values4': data_list4,
                        })
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)