from flask import Blueprint, request, jsonify
from capstone_design import mongo

patient_bp = Blueprint('patient', __name__)

# 환자 등록
@patient_bp.route('/my_patient', methods=['POST'])
def register_patient():
    data = request.json
    patient_name = data.get('patient_name')
    patient_age = data.get('patient_age')
    
    p_id = mongo.db.patients.estimated_document_count() + 1
    mongo.db.patients.insert_one({
        'p_id': p_id,
        'patient_name': patient_name,
        'patient_age': patient_age
    })

    return jsonify({'message': 'successful', 'patient_id' : p_id}), 201

# 환자 삭제
@patient_bp.route('/delete_patient/<int:p_id>', methods=['DELETE'])
def delete_patient(p_id):
    result = mongo.db.patients.delete_one({'p_id': p_id})

    if result.deleted_count == 0:
        return jsonify({'error': 'PatientNot_found'}), 404

    return jsonify({'message': 'successful'}), 200

# 환자 목록 조회
@patient_bp.route('/patient_list', methods=['GET'])
def list_patients():
    patients = list(mongo.db.patients.find({}, {'_id': 0}))
    if not patients:
        return jsonify({'error': 'PatientNot_found'}), 404

    return jsonify(patients), 200
