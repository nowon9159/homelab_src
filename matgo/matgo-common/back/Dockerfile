# Stage 1: Build stage
FROM openjdk:17-slim AS build

# 작업 디렉토리 생성
WORKDIR /app

# Gradle 캐시를 활용하기 위해 먼저 Gradle Wrapper와 의존성 파일만 복사
COPY gradlew gradlew
COPY gradle gradle
COPY build.gradle settings.gradle ./

# Gradle 실행 권한 부여
RUN chmod +x gradlew

# 의존성 미리 다운로드
RUN ./gradlew dependencies --no-daemon || return 0

# 프로젝트 전체 복사
COPY . .

# 빌드 수행
RUN ./gradlew build --no-daemon

# Stage 2: Runtime stage
FROM openjdk:17-slim

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 산출물 복사
COPY --from=build /app/build/libs/*.jar app.jar

# 애플리케이션 실행
ENTRYPOINT ["java", "-jar", "app.jar"]
