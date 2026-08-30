import os
import time
import json
import io
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 업로드 폴더 설정 (Render 서버 내 저장 -> 404 및 API 에러 완벽 방지)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"users": {}, "boards": [{"id": "board1", "name": "우리반 게시판"}], "posts": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

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
