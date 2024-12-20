# Python 3.9 Slim 버전 사용
FROM python:3.9-slim

# OS 기본 종속성 설치 (TensorFlow 관련)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 복사
COPY capstone_design/ ./capstone_design

# 두 번째 시도
# Flask 설정
ENV FLASK_APP=capstone_design.run
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0

# 포트 열기
EXPOSE 5000

# 애플리케이션 실행
CMD ["flask", "run"]
