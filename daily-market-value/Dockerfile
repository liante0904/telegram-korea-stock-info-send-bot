# Dockerfile
# Python 3.10 베이스 이미지 사용
FROM python:3.10.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY .env /app/.env
COPY requirements.txt requirements.txt
COPY . .

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt


# 기본 명령으로 대기 상태 설정
CMD ["tail", "-f", "/dev/null"]