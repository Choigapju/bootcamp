# 부트캠프 지원서 평가 시스템 - 빠른 시작 가이드

이 가이드는 macOS 환경의 VSCode에서 부트캠프 지원서 평가 시스템을 빠르게 설정하고 실행하는 방법을 안내합니다.

## 1. 환경 설정

### VSCode에서 작업 폴더 열기

1. VSCode를 실행합니다.
2. `File > Open Folder`를 선택하고 프로젝트 폴더를 생성하거나 선택합니다.

### 터미널 열기

1. VSCode에서 `` Ctrl + ` ``를 눌러 내장 터미널을 엽니다.

### 가상 환경 설정

```bash
# 가상 환경 폴더 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 버전 확인
python --version  # Python 3.8 이상이어야 합니다
```

## 2. 프로젝트 파일 생성

### 폴더 구조 생성

```bash
# 필요한 디렉토리 생성
mkdir -p models static/css static/js templates uploads
```

### 필요한 파일 복사

1. 제공된 모든 코드 파일을 해당 위치에 복사합니다:
   - `app.py` (루트 폴더)
   - `models/evaluator.py`
   - `static/css/style.css`
   - `static/js/script.js`
   - 모든 HTML 템플릿을 `templates/` 폴더에 복사
   - `requirements.txt` (루트 폴더)

## 3. 종속성 설치

```bash
# requirements.txt에 나열된 모든 패키지 설치
pip install -r requirements.txt
```

## 4. 애플리케이션 실행

```bash
# Flask 개발 서버 실행
python app.py
```

웹 브라우저에서 `http://127.0.0.1:5000/`로 접속합니다.

## 5. 사용 방법

### 모델 훈련 (필수 첫 단계)

1. '모델 훈련' 메뉴를 클릭합니다.
2. 지시에 따라 CSV 훈련 데이터를 업로드합니다.
   - 'text' 컬럼: 지원서 내용
   - 'employment' 컬럼: 취업 성공 여부 ('success'/'yes' 또는 기타)

### 지원서 평가

1. 모델 훈련 후 '파일 평가' 또는 '텍스트 평가' 메뉴로 이동합니다.
2. CSV 파일 업로드 또는 텍스트 직접 입력을 통해 평가를 진행합니다.
3. 결과를 분석하고 필요에 따라 CSV로 다운로드합니다.

## 6. 문제 해결

### 모델 훈련 오류

훈련 데이터가 올바른 형식인지 확인하세요:
- 'text' 컬럼: 지원서 텍스트 (필수)
- 'employment' 컬럼: 'success'/'yes' 또는 기타 값 (필수)

### 파일 평가 오류

CSV 파일이 올바른 형식인지 확인하세요:
- 텍스트 필드가 포함되어 있어야 합니다 (기본적으로 21번째 컬럼 이후 모두 사용)
- '합불상태' 컬럼이 있다면 '검토전' 또는 '합격' 상태의 지원자만 평가됩니다.

### 기타 오류

콘솔 로그를 확인하여 오류 메시지를 확인하세요. 필요한 경우 디버그 모드를 활성화합니다:

```python
# app.py에서
if __name__ == '__main__':
    app.run(debug=True)
```