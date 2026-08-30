import os
import json
import sqlite3
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'mypadlet_secret_key_123'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_FILE = 'mypadlet.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id TEXT PRIMARY KEY,
            pw TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board_id INTEGER NOT NULL,
            section TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            files TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# --- 교사 회원가입 API ---
@app.route('/api/teacher/register', methods=['POST'])
def register_teacher():
    data = request.json
    t_id = data.get('id')
    t_pw = data.get('pw')
    t_name = data.get('name')
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO teachers (id, pw, name) VALUES (?, ?, ?)', (t_id, t_pw, t_name))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '교사 회원가입이 완료되었습니다.'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': '이미 존재하는 아이디이거나 오류가 발생했습니다.'})

# --- 교사 로그인 API ---
@app.route('/api/teacher/login', methods=['POST'])
def login_teacher():
    data = request.json
    t_id = data.get('id')
    t_pw = data.get('pw')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teachers WHERE id = ? AND pw = ?', (t_id, t_pw))
    teacher = cursor.fetchone()
    conn.close()
    
    if teacher:
        session['teacher_id'] = teacher['id']
        session['teacher_name'] = teacher['name']
        return jsonify({'success': True, 'name': teacher['name']})
    else:
        return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 일치하지 않습니다.'})

# --- 파일 업로드 (서버 저장 -> 404 에러 방지) ---
@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    uploaded_urls = []
    uploaded_files = []
    
    for file in files:
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1]
            if not ext: ext = '.png'
            
            save_name = f"{int(time.time() * 1000)}_{os.urandom(4).hex()}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
            file.save(filepath)
            
            url = f"/static/uploads/{save_name}"
            uploaded_urls.append(url)
            uploaded_files.append({"url": url, "name": file.filename})
            
    return jsonify({'urls': uploaded_urls, 'files': uploaded_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
