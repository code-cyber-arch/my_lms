from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import User, Course, Enrollment, Content, Assessment

main_bp = Blueprint('main', __name__)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data['role']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        if user and user.password == data['password']:
            access_token = create_access_token(identity={'id': user.id, 'role': user.role})
            response = redirect(url_for('main.get_courses'))
            response.set_cookie('access_token', access_token)
            return response
        return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@main_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

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
