from flask import Blueprint, request, jsonify
from capstone_design import mongo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    user_pw = data.get('user_pw')
    
    if not user_id or not user_pw:
        return jsonify({'error': 'ID and PW are required'}), 400
    
    user = mongo.db.user.find_one({'user_id': user_id})
    if not user:
        return jsonify({'error': 'IDisNOT_exist'}), 404

    if user['user_pw'] != user_pw:
        return jsonify({'error': 'PWDoesntMatch'}), 401

    return jsonify({'message': 'successful', 'user_id': user_id}), 200
##########로그인 응답요청은 건드리지 말것 ####
