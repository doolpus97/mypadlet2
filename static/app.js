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
            window.location.href = '/board';
        } else {
            alert(data.message);
        }
    });
    return false;
}

// 학생 입장
function handleStudentLogin(event) {
    event.preventDefault();
    const code = document.getElementById('entryCode').value;
    const name = document.getElementById('studentName').value;

    fetch('/api/student/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, name })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/board';
        } else {
            alert('입장 코드가 올바르지 않습니다.');
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
