from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from collections import defaultdict
from capstone_design import mongo
import os

records_bp = Blueprint('records', __name__)


# **1. 일별 조회**
@records_bp.route('/daily_stats', methods=['GET'])
def daily_stats():
    p_id = request.args.get('p_id')
    date_data = request.args.get('date') 
   
    if date_data:
        date_data = datetime.strptime(date_data, '%Y-%m-%d')
    else:
        date_data = datetime.now() # `date_data`가 없는 경우 오늘 날짜로 설정

    # 지정된 날짜의 시작 시간과 종료 시간 계산하는 로직
    start_of_day = date_data.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = date_data.replace(hour=23, minute=59, second=59, microsecond=999999)

    daily_records = list(mongo.db.record_mypoop.find({
        'p_id': int(p_id),
        'start_time': {'$gte': start_of_day, '$lte': end_of_day}
    }))
    
    if not daily_records: #해당 날짜의 데이터가 없으면 에러를 반환한다!
        return jsonify({'error': 'NoRecords'}), 404

    bristol_list = [record['bristol_scale'] for record in daily_records] #배변 횟수만큼 
    time_info = [{
        'starttime': record['start_time'].strftime('%Y-%m-%d %H:%M:%S'),#배변 시작시간과
        'endtime': record['end_time'].strftime('%Y-%m-%d %H:%M:%S'),#배변 종료시간과
        'duration': record['duration']#배변하는데 걸린 시간을 배열로 반환
    } for record in daily_records]

    result = {
        #'date': date_data.strftime('%Y-%m-%d'),
        'bristol': bristol_list, #브리스톨 단계
        'count': len(daily_records), #하룻동안 배변 횟수
        'time_info': time_info #시간정보들(배열)
    }

    return jsonify(result), 200 #결과값 반환


# **2. 월별 조회**
@records_bp.route('/monthly_stats', methods=['GET'])
def monthly_stats():
    p_id = request.args.get('p_id')
    p_id = int(p_id)
    
    current_time = datetime.now()
    year = request.args.get('year', current_time.year, type=int) #받아온 파라미터를 정수로 변경
    month = request.args.get('month', current_time.month, type=int)

    first_day_of_month = datetime(year, month, 1) #해당 월의 첫째날 계산
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1) #해당 월의 마지막날

    monthly_records = list(mongo.db.record_mypoop.find({
        'p_id': int(p_id), #db에서 해당 환자 id와 날짜 추출하기
        'start_time' : {'$gte': first_day_of_month, '$lte': last_day_of_month}
    }))

    if not monthly_records:
        return jsonify({'error': 'NoRecords'}), 404 #해당 월의 데이터가 하나~도 없으면 에러 반환한다!

    bristol_scale_counts = defaultdict(int)
    total_duration = 0

    for record in monthly_records:
        bristol = record.get('bristol_scale')
        duration = record.get('duration')
        timestamp = record.get('timestamp')

        total_duration += duration
        bristol_scale_counts[bristol] += 1
       
    most_frequent_bristol = max(bristol_scale_counts, key=bristol_scale_counts.get) if bristol_scale_counts else None #최다 브리스톨값 계산
    bristol_1_2 = bristol_scale_counts[1] + bristol_scale_counts[2] #브리스톨 1,2형 합 계산
    bristol_6_7 = bristol_scale_counts[6] + bristol_scale_counts[7] #브리스톨 6,7형 합 계산
    average_duration = total_duration / len(monthly_records) if monthly_records else 0 #평균 배변 시간 계산
    
    result = {#결과값 : 
        'most_frequent_bristol': most_frequent_bristol, #월 최다 브리스톨 단계
        'average_duration': round(average_duration, 2), # 평균 배변 시간
        'bristol_1_2': bristol_1_2, #한달동안 브리스톨 1~2형이 나온 횟수 (변비)
        'bristol_6_7': bristol_6_7, #한달동안 브리스톨 6~7형이 나온 횟수 (설사)
        'most_frequent_color': 0
    }

    return jsonify(result), 200

