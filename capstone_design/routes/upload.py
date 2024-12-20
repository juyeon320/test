
"""
from ultralytics import YOLO
from collections import Counter
import os
import base64
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from capstone_design import mongo  # MongoDB 연결

# !!! 모델 저장위치 바꿔야함
model_path = "capstone_design/models/best.pt"
model = YOLO(model_path)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # 업로드 폴더 설정
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/record_poop', methods=['POST'])
def record_poop_with_image():
    try:
        # 이미지 데이터 및 메타데이터 가져오기
        img_name = request.form.get('img')  # 이미지 파일 이름
        filetype = request.form.get('filetype')  # 파일 유형
        filedata = request.form.get('filedata')  # Base64 인코딩된 파일 데이터
        upload_date = request.form.get('upload_date')  # 업로드 날짜

        if not img_name or not filedata:
            return jsonify({'error': 'Missing image data or file name'}), 400

        # Base64 디코딩하여 파일 저장
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, img_name)
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(filedata))
        print(f"File saved at {file_path}")

        # YOLO 모델 실행
        results = model(file_path)
        class_name = ["1", "2", "3", "4", "5", "6", "7"]
        predicted_classes = []

        for result in results:
            for box in result.boxes:
                cls = int(box.cls.numpy().item())
                predicted_classes.append(cls)

        if not predicted_classes:
            return jsonify({'error': 'No predictions made'}), 400

        counter = Counter(predicted_classes)
        most_common_idx = counter.most_common(1)[0][0]
        most_common_class = class_name[most_common_idx]
        print(f"Predicted Bristol scale: {most_common_class}")

        # MongoDB에 데이터 저장
        try:
            mongo.db.record_mypoop.insert_one({
                'p_id': int(request.form.get('p_id', 3)),  # 요청에서 p_id를 받거나 기본값 3
                'timestamp': datetime.now(),
                'start_time': datetime.strptime(request.form.get('start_time', "2024-11-26 11:11:11"), '%Y-%m-%d %H:%M:%S'),
                'end_time': datetime.strptime(request.form.get('end_time', "2024-11-26 11:11:11"), '%Y-%m-%d %H:%M:%S'),
                'duration': 0,
                'bristol_scale': most_common_class,
                'file_path': file_path,
            })
            print("Data saved to MongoDB")
        except Exception as e:
            print(f"Error saving to MongoDB: {str(e)}")
            return jsonify({'error': f'MongoDB error: {str(e)}'}), 500

        return jsonify({
            'message': 'successful',
            'bristol_scale': most_common_class,
            'file_path': file_path
        }), 200

    except ValueError as ve:
        print(f"ValueError: {str(ve)}")
        return jsonify({'error': 'Invalid time format. Use YYYY-MM-DD HH:MM:SS'}), 400
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
"""

from ultralytics import YOLO
from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import base64
from collections import Counter
from capstone_design import mongo  # MongoDB 연결

# 모델 경로 및 업로드 폴더 설정
MODEL_PATH = "capstone_design/models/best.pt"
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

# YOLO 모델 로드
model = YOLO(MODEL_PATH)

# Flask Blueprint 설정
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/record_poop', methods=['POST'])
def record_poop():
    try:
        # 요청 데이터 가져오기
        img_name = request.form.get('img')  # 이미지 파일 이름
        #filetype = request.form.get('filetype')  # 파일 유형
        filedata = request.form.get('filedata')  # Base64 인코딩된 파일 데이터
        #upload_date = request.form.get('upload_date')  # 업로드 날짜

        # 요청 데이터 검증
        if not img_name or not filedata:
            return jsonify({'error': 'Missing image name or data'}), 400
        print(f"Received img_name: {img_name}, filetype: {filetype}, upload_date: {upload_date}")

        # Base64 디코딩하여 파일 저장
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, img_name)
        try:
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(filedata))
            print(f"File saved successfully at {file_path}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

        # YOLO 모델로 예측 수행
        try:
            results = model(file_path)
            print(f"YOLO model results: {results}")
        except Exception as e:
            print(f"Error processing image with YOLO model: {str(e)}")
            return jsonify({'error': f'YOLO model error: {str(e)}'}), 500

        # 클래스 매핑 리스트
        class_name = ["1", "2", "3", "4", "5", "6", "7"]
        predicted_classes = []

        for result in results:
            for box in result.boxes:
                cls = int(box.cls.numpy().item())
                predicted_classes.append(cls)

        if not predicted_classes:
            return jsonify({'error': 'No predictions made'}), 400

        # 최빈값 계산
        counter = Counter(predicted_classes)
        most_common_idx = counter.most_common(1)[0][0]
        most_common_class = class_name[most_common_idx]
        print(f"Predicted bristol scale: {most_common_class}")

        # MongoDB에 데이터 저장
        try:
            mongo.db.record_mypoop.insert_one({
                'timestamp': datetime.now(),
                'upload_date': upload_date,
                'filetype': filetype,
                'bristol_scale': most_common_class,
                'file_path': file_path,
            })
            print(f"Data saved to MongoDB successfully")
        except Exception as e:
            print(f"Error saving to MongoDB: {str(e)}")
            return jsonify({'error': f'Failed to save to MongoDB: {str(e)}'}), 500

        # 성공 응답 반환
        return jsonify({
            'message': 'Successful',
            'bristol_scale': most_common_class,
            'file_path': file_path
        }), 200

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
