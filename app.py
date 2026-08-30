import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect

app = Flask(__name__)
app.secret_key = 'mypadlet_secret_key_123'

DATA_FILE = 'teachers.json'

def load_teachers():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_teachers(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/board')
def board():
    return render_template('board.html')

@app.route('/api/teacher/register', methods=['POST'])
def register_teacher():
    data = request.json
    t_id = data.get('id')
    t_pw = data.get('pw')
    t_name = data.get('name')
    teachers = load_teachers()
    
    if t_id in teachers:
        return jsonify({'success': False, 'message': '이미 존재하는 아이디입니다.'})
        
    teachers[t_id] = {'pw': t_pw, 'name': t_name}
    save_teachers(teachers)
    return jsonify({'success': True, 'message': '회원가입이 완료되었습니다.'})

@app.route('/api/teacher/login', methods=['POST'])
def login_teacher():
    data = request.json
    t_id = data.get('id')
    t_pw = data.get('pw')
    teachers = load_teachers()
    
    if t_id in teachers and teachers[t_id]['pw'] == t_pw:
        session['user_type'] = 'teacher'
        session['user_name'] = teachers[t_id]['name']
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 일치하지 않습니다.'})

@app.route('/api/student/login', methods=['POST'])
def login_student():
    data = request.json
    session['user_type'] = 'student'
    session['user_name'] = data.get('name')
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
