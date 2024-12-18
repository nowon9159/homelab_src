# Stage 1: Build stage
FROM node:22.12.0-slim AS build

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 lock 파일만 복사해서 의존성 캐시 활용
COPY package*.json ./

# 의존성 설치
RUN npm install

# Vue.js 소스 복사
COPY . .

# 빌드 수행
RUN npm run build

# Stage 2: Runtime stage
FROM node:22.12.0-slim

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 산출물만 복사
COPY --from=build /app/dist ./dist

# 종속성 복사를 최소화하기 위해 프로덕션 모드 의존성만 설치
COPY package*.json ./
RUN npm install --only=production

# Vue.js 애플리케이션을 실행하는 Node.js 서버 실행
CMD ["npx", "serve", "dist"]
