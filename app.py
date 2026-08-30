import os
import time
import json
import io
from flask import Flask, render_template, request, jsonify

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = Flask(__name__)

FOLDER_ID = '1capKURBOv5TpP0DgNvagP8VQYfnLlBtl'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    try:
        creds_json = os.environ.get('GDRIVE_CREDENTIALS')
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES)
            return build('drive', 'v3', credentials=creds)
        return None
    except Exception as e:
        print("구글 드라이브 인증 오류:", e)
        return None

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
    return {"users": {}, "boards": [], "posts": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    uploaded_urls = []
    uploaded_files = []
    
    drive_service = get_drive_service()
    
    for file in files:
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1]
            if not ext: ext = '.png'
            
            save_name = f"{int(time.time() * 1000)}_{os.urandom(4).hex()}{ext}"
            saved_to_drive = False

            # 구글 드라이브 업로드 시도
            if drive_service:
                try:
                    file_stream = io.BytesIO(file.read())
                    media = MediaIoBaseUpload(file_stream, mimetype=file.mimetype, resumable=True)
                    
                    file_metadata = {
                        'name': save_name,
                        'parents': [FOLDER_ID]
                    }
                    
                    uploaded_file = drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    file_id = uploaded_file.get('id')
                    url = f"https://drive.google.com/uc?id={file_id}"
                    uploaded_urls.append(url)
                    uploaded_files.append({"url": url, "name": file.filename})
                    saved_to_drive = True
                except Exception as e:
                    print("구글 드라이브 업로드 실패, 로컬 폴더로 대체 저장합니다:", e)

            # 구글 드라이브 연동 실패 시 안전한 로컬 저장 (404 방지)
            if not saved_to_drive:
                file.seek(0)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
                file.save(filepath)
                url = f"/static/uploads/{save_name}"
                uploaded_urls.append(url)
                uploaded_files.append({"url": url, "name": file.filename})
            
    return jsonify({'urls': uploaded_urls, 'files': uploaded_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)