// 교사 로그인
function handleTeacherLogin(event) {
    event.preventDefault();
    const id = document.getElementById('teacherId').value;
    const pw = document.getElementById('teacherPw').value;

    fetch('/api/teacher/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, pw })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showBoard(data.name, '교사');
        } else {
            alert(data.message);
        }
    });
    return false;
}

// 학생 입장
function handleStudentLogin(event) {
    event.preventDefault();
    const name = document.getElementById('studentName').value;

    fetch('/api/student/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showBoard(data.name, '학생');
        }
    });
    return false;
}

// 교사 회원가입
function handleTeacherRegister(event) {
    event.preventDefault();
    const id = document.getElementById('regTeacherId').value;
    const pw = document.getElementById('regTeacherPw').value;
    const name = document.getElementById('regTeacherName').value;

    fetch('/api/teacher/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, pw, name })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            const teacherTab = new bootstrap.Tab(document.getElementById('teacher-tab'));
            teacherTab.show();
        }
    });
    return false;
}

// 로그인 성공 시 화면 전환 함수
function showBoard(userName, userRole) {
    document.getElementById('loginSection').classList.add('d-none');
    document.getElementById('boardSection').classList.remove('d-none');
    document.getElementById('userInfo').innerText = `${userName} (${userRole})`;
}
