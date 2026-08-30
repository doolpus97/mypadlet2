import os
import time
import json
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'mypadlet_secret_key_123'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# 교사 회원가입 API
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
    return jsonify({'success': True, 'message': '교사 회원가입이 완료되었습니다! 로그인해 주세요.'})

# 사진/파일 업로드 API (서버 직접 저장으로 404 방지)
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
