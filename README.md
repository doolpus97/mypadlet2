# MyPadlet 2 - Python + Flask + SQLite

Padlet과 비슷한 교실용 게시판입니다. **교사용 Windows PC 자체가 서버**가 되고, 기본 데이터 저장소는 `D:\MyPadlet`입니다.

## 이번 버전에 추가된 기능

- Padlet 스타일 섹션형 보드
- `＋ 게시` 버튼
- 제목 / 내용 입력
- 사진 / 비디오 / 오디오 업로드
- PDF, Word, PowerPoint, Excel, TXT, CSV 업로드
- 모바일·태블릿의 `📷 사진 촬영` 버튼으로 카메라 입력
- 링크 추가
- Google 이미지 검색
  - API 설정 시 앱 내부 썸네일 검색
  - API 미설정 시 Google Images 새 탭 열기
- 게시물 수정 / 삭제
  - 학생: 본인이 만든 게시물만 수정·삭제
  - 교사: 모든 게시물 수정·삭제
- 섹션 추가 / 이름 변경 / 삭제
- **교사 전용 드래그앤드롭**으로 게시물과 섹션 순서 변경
- 게시판 제목 / 배경 설정
- **3초 자동 새로고침**으로 같은 LAN 학생 기기 사이의 간단한 실시간 동기화
- SQLite 저장
- `D:\MyPadlet\uploads`에 파일 저장
- `D:\MyPadlet\backup\board.json` 자동 백업
- 선택적으로 Google Drive에도 `board.json` 백업 가능
- 학교 Wi-Fi에서 학생 태블릿이 교사 PC의 IP로 접속 가능
- 교사 PIN 로그인

> 이 프로젝트는 **교실 내부 네트워크용 MVP**입니다. 인터넷에 공개하려면 HTTPS, 사용자 계정, CSRF, 악성 파일 검사, 더 강한 인증 등을 추가해야 합니다.

## 1. 설치

Windows PowerShell에서 프로젝트 폴더로 이동 후:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. 교사 PIN 변경

기본 PIN은 `1234`입니다. `run_mypadlet.bat`는 예시로 `2468`을 사용합니다. 실제 사용 전에 원하는 PIN으로 변경하는 것을 권장합니다.

PowerShell 예:

```powershell
$env:MYPADLET_TEACHER_PIN="내가정한PIN"
$env:MYPADLET_SECRET_KEY="길고임의의문자열"
python app.py
```

## 3. 실행

가장 간단한 방법은 폴더 안의 `run_mypadlet.bat`를 더블클릭하는 것입니다. 첫 실행 시 가상환경과 필요한 Python 패키지를 자동으로 설치합니다.

또는 PowerShell에서 직접:

```powershell
python app.py
```

교사 PC:

```text
http://127.0.0.1:5000
```

같은 학교 Wi-Fi의 태블릿은 교사 PC의 내부 IP가 예를 들어 `192.168.0.10`일 경우:

```text
http://192.168.0.10:5000
```

### Windows 방화벽

처음 실행할 때 Python의 네트워크 액세스를 허용하고, 가능하면 학교의 **개인 네트워크**에서만 허용하세요.

## 4. 저장 위치

기본:

```text
D:\MyPadlet\mypadlet.db
D:\MyPadlet\uploads\
D:\MyPadlet\backup\board.json
```

D드라이브가 없으면:

```powershell
$env:MYPADLET_DATA_DIR="C:\MyPadlet"
python app.py
```

## 5. Google 이미지 검색

앱 내부에서 Google 이미지 결과를 가져오려면 Google Custom Search JSON API와 Programmable Search Engine을 설정합니다.

```powershell
$env:GOOGLE_API_KEY="YOUR_KEY"
$env:GOOGLE_CSE_ID="YOUR_CSE_ID"
python app.py
```

설정하지 않아도 Google 이미지 검색 버튼은 새 탭으로 검색 페이지를 엽니다.

## 6. Google Drive 자동 백업(선택)

이 기능은 **Google Drive를 웹 서버로 사용하는 것이 아니라, 백업 저장소로 사용하는 기능**입니다.

가장 단순한 구성은 Google Cloud에서 서비스 계정의 JSON 키를 만들고, Google Drive에서 백업 폴더를 그 서비스 계정 이메일과 공유하는 것입니다.

```powershell
$env:GOOGLE_SERVICE_ACCOUNT_JSON="C:\Keys\mypadlet-service-account.json"
$env:GOOGLE_DRIVE_FOLDER_ID="GoogleDrive폴더ID"
python app.py
```

변경이 발생할 때 `D:\MyPadlet\backup\board.json`이 먼저 갱신되고, Google Drive 설정이 되어 있으면 같은 `board.json`을 지정 폴더에 업로드/업데이트합니다.

## 7. 기능 사용법

### 학생

- 웹 주소로 접속
- `＋ 게시` 선택
- 섹션 / 제목 / 내용 입력
- 사진, 동영상, 오디오, PDF/문서, 카메라, 링크, Google 이미지 사용
- 자신이 올린 게시물은 수정/삭제 가능

### 교사

- `교사 로그인` → PIN 입력
- 섹션 추가 / 삭제 / 이름 변경
- 게시판 제목 및 배경 변경
- 게시물과 섹션 드래그앤드롭
- 모든 게시물 수정/삭제
- 교사 로그아웃 시 학생 모드로 돌아감

## 8. 실시간 동기화 방식

별도의 WebSocket 서버를 추가하지 않고 브라우저가 기본 **3초마다 `/api/board`를 조회**합니다.

따라서 한 학생이 게시물을 올리면 다른 학생 기기에도 최대 약 3초 안에 표시됩니다.

실시간 수십 번/초 수준의 협업이 필요하면 이후에 Socket.IO 또는 WebSocket 서버로 교체하는 것이 좋습니다.

## 9. 보안 주의

인터넷에 그대로 공개하지 마세요.

외부 공개 서비스로 전환하려면 최소한:

- HTTPS
- 사용자별 계정
- 강한 교사 인증
- CSRF 방어
- 업로드 파일 악성코드 검사
- 파일별 MIME/크기 검증 강화
- 권한별 API 보호
- 데이터베이스 백업 전략

이 필요합니다.
