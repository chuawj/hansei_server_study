# 1. 어떤 환경에서 실행할지 명시
FROM python:3.10-slim

# 2. 작업 폴더 생성 및 설정
WORKDIR /app

# 3. 필요 패키지 파일 먼저 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 앱 소스 코드 복사
COPY app.py .

# 5. 컨테이너 시작 시 실행할 명령 지정
CMD ["python", "app.py"]