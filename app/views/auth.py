from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.controllers.auth import AuthController
from app.schemas.auth import LoginSchema, RegisterSchema, PasswordResetSchema, PasswordChangeSchema

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
auth_controller = AuthController()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        schema = RegisterSchema()
        data = schema.load(request.get_json())
        response, status_code = auth_controller.register(data)
        return jsonify(response), status_code
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json())
        response, status_code = auth_controller.login(data)
        return jsonify(response), status_code
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        schema = PasswordResetSchema()
        data = schema.load(request.get_json())
        response, status_code = auth_controller.reset_password(
            data['token'], 
            data['new_password']
        )
        return jsonify(response), status_code
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        schema = PasswordChangeSchema()
        data = schema.load(request.get_json())
        user_id = get_jwt_identity()
        response, status_code = auth_controller.change_password(
            user_id,
            data['current_password'],
            data['new_password']
        )
        return jsonify(response), status_code
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    response, status_code = auth_controller.get_profile(user_id)
    return jsonify(response), status_code

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        response, status_code = auth_controller.update_profile(user_id, data)
        return jsonify(response), status_code
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400