from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import User, Course, Enrollment, Content, Assessment

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return 'Welcome to my LMS'

@main_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully', 'user': {
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email,
        'role': new_user.role,
        'created_at': new_user.created_at
    }})

@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'message': 'Login successful', 'access_token': access_token, 'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }})
    return jsonify({'message': 'Invalid credentials'}), 401

@main_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    current_user = get_jwt_identity()
    if current_user['role'] != 'instructor':
        return jsonify({'message': 'Permission denied'}), 403
    data = request.get_json()
    new_course = Course(
        title=data['title'],
        description=data['description'],
        instructor_id=current_user['id']
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({'message': 'Course created successfully', 'course': {
        'id': new_course.id,
        'title': new_course.title,
        'description': new_course.description,
        'instructor_id': new_course.instructor_id,
        'created_at': new_course.created_at
    }})

@main_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()
    return jsonify([{
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'instructor_id': course.instructor_id,
        'created_at': course.created_at
    } for course in courses])