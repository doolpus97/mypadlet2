import os
import time
import json
import io
from flask import Flask, render_template, request, jsonify

# 구글 드라이브 연동 라이브러리
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = Flask(__name__)

# ================= 구글 드라이브 설정 =================
# 구글 드라이브 폴더 ID (드라이브 주소창에서 복사해서 아래에 붙여넣으세요)
FOLDER_ID = '1capKURBOv5TpP0DgNvagP8VQYfnLlBtl' 
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    try:
        # 깃허브에 파일로 올리지 않고, 클라우드 서버의 '비밀 환경변수'에서 키를 읽어옵니다.
        creds_json = os.environ.get('GDRIVE_CREDENTIALS')
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES)
            return build('drive', 'v3', credentials=creds)
        else:
            print("환경변수에 구글 드라이브 인증 정보가 없습니다.")
            return None
    except Exception as e:
        print("구글 드라이브 인증 오류:", e)
        return None
# ====================================================

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
            
            # 클라우드 서버 환경: 구글 드라이브 서비스가 연결된 경우
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
                except Exception as e:
                    print("구글 드라이브 업로드 실패:", e)
            else:
                # 로컬 테스트용 폴더 저장 (드라이브 연동 전)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
                file.save(filepath)
                url = f"/static/uploads/{save_name}"
                uploaded_urls.append(url)
                uploaded_files.append({"url": url, "name": file.filename})

    return jsonify({'urls': uploaded_urls, 'files': uploaded_files})

# ================= 백엔드 API =================
@app.route('/api/login/teacher', methods=['POST'])
def login_teacher():
    data = request.json or {}
    teacher_id = data.get('teacherId', '').strip()
    teacher_pw = data.get('teacherPw', '').strip()
    
    if not teacher_id:
        return jsonify({'success': False, 'message': '아이디를 입력하세요.'}), 400
        
    if teacher_id not in db['users']:
        db['users'][teacher_id] = teacher_pw
        save_data(db)
    
    return jsonify({'success': True, 'teacherId': teacher_id})

@app.route('/api/boards', methods=['GET'])
def get_boards():
    teacher_id = request.args.get('teacherId', '').strip()
    if teacher_id:
        teacher_boards = [b for b in db['boards'] if b.get('owner') == teacher_id]
        return jsonify({'boards': teacher_boards})
    return jsonify({'boards': db['boards']})

@app.route('/api/boards/by_code', methods=['GET'])
def get_board_by_code():
    code = request.args.get('code', '').strip()
    board = next((b for b in db['boards'] if b.get('code') == code), None)
    if board:
        return jsonify({'success': True, 'board': board})
    return jsonify({'success': False, 'message': '입장 코드에 해당하는 게시판이 없습니다.'}), 404

@app.route('/api/boards', methods=['POST'])
def create_board():
    data = request.json or {}
    title = data.get('title', '').strip()
    code = data.get('code', '').strip()
    teacher_id = data.get('teacherId', '').strip()
    
    if not title or not code:
        return jsonify({'success': False, 'message': '제목과 코드를 입력하세요.'}), 400
        
    new_board = {
        'id': f"board_{int(time.time()*1000)}",
        'title': title,
        'code': code,
        'owner': teacher_id
    }
    db['boards'].append(new_board)
    save_data(db)
    return jsonify({'success': True, 'board': new_board})

@app.route('/api/boards/code', methods=['PUT'])
def update_board_code():
    data = request.json or {}
    board_title = data.get('title', '').strip()
    new_code = data.get('code', '').strip()
    
    for b in db['boards']:
        if b['title'] == board_title:
            b['code'] = new_code
            break
    save_data(db)
    return jsonify({'success': True})

@app.route('/api/posts', methods=['GET'])
def get_posts():
    board_title = request.args.get('boardTitle', '').strip()
    posts = db['posts'].get(board_title, [])
    return jsonify({'posts': posts})

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.json or {}
    board_title = data.get('boardTitle', '').strip()
    if not board_title:
        return jsonify({'success': False, 'message': '게시판 정보가 필요합니다.'}), 400
        
    if board_title not in db['posts']:
        db['posts'][board_title] = []
        
    post = {
        'postId': f"post_{int(time.time()*1000)}_{os.urandom(2).hex()}",
        'sectionId': data.get('sectionId'),
        'author': data.get('author'),
        'title': data.get('title'),
        'content': data.get('content'),
        'imgs': data.get('imgs', []),
        'links': data.get('links', []),
        'attachedFiles': data.get('attachedFiles', []),
        'comments': []
    }
    db['posts'][board_title].insert(0, post)
    save_data(db)
    return jsonify({'success': True, 'post': post})

@app.route('/api/posts/move', methods=['PUT'])
def move_post():
    data = request.json or {}
    board_title = data.get('boardTitle', '').strip()
    post_id = data.get('postId', '').strip()
    new_section = data.get('sectionId', '').strip()
    
    posts = db['posts'].get(board_title, [])
    for p in posts:
        if p['postId'] == post_id:
            p['sectionId'] = new_section
            break
    save_data(db)
    return jsonify({'success': True})

@app.route('/api/posts/edit', methods=['PUT'])
def edit_post():
    data = request.json or {}
    board_title = data.get('boardTitle', '').strip()
    post_id = data.get('postId', '').strip()
    new_title = data.get('title')
    new_content = data.get('content')
    new_imgs = data.get('imgs')
    new_links = data.get('links')
    new_attachedFiles = data.get('attachedFiles')
    
    posts = db['posts'].get(board_title, [])
    for p in posts:
        if p['postId'] == post_id:
            p['title'] = new_title
            p['content'] = new_content
            if new_imgs is not None:
                p['imgs'] = new_imgs
            if new_links is not None:
                p['links'] = new_links
            if new_attachedFiles is not None:
                p['attachedFiles'] = new_attachedFiles
            break
    save_data(db)
    return jsonify({'success': True})

@app.route('/api/posts', methods=['DELETE'])
def delete_post():
    data = request.json or {}
    board_title = data.get('boardTitle', '').strip()
    post_id = data.get('postId', '').strip()
    
    if board_title in db['posts']:
        db['posts'][board_title] = [p for p in db['posts'][board_title] if p['postId'] != post_id]
        save_data(db)
    return jsonify({'success': True})

@app.route('/api/comments', methods=['POST'])
def add_comment():
    data = request.json or {}
    board_title = data.get('boardTitle', '').strip()
    post_id = data.get('postId', '').strip()
    author = data.get('author', '').strip()
    text = data.get('text', '').strip()
    
    posts = db['posts'].get(board_title, [])
    for p in posts:
        if p['postId'] == post_id:
            if 'comments' not in p:
                p['comments'] = []
            p['comments'].append({'author': author, 'text': text})
            break
    save_data(db)
    return jsonify({'success': True})

if __name__ == '__main__':
    # 클라우드 서버 환경에 맞게 포트 바인딩 수정
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)