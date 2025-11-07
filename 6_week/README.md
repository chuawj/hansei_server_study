# Ubuntu 실시간 웹(학습용) — 따라하기 가이드

이 리포지토리는 Ubuntu 기반 Docker 컨테이너 안에서 실행되는 간단한 실시간 웹 애플리케이션(Express + Socket.IO)을 제공합니다. 스터디 참가자가 따라할 수 있도록 설치, 실행, 테스트, 문제 해결 방법을 단계별로 정리했습니다.

---

## 목차
- 개요
- 요구사항
- 파일 구조 설명
- 실행 방법 (Windows PowerShell / cmd)
- 동작 확인(테스트)
- 자주 발생하는 문제와 해결 방법
- 확장 과제(학습용)

---

## 개요
이 프로젝트는 로컬 개발 환경에서 실시간 상호작용을 실습하기 위한 샘플입니다. 클라이언트는 `public/index.html`을 통해 Socket.IO로 서버와 실시간 메시지를 주고받습니다.

서버 핵심 파일: `server.js` (Express + Socket.IO)
Docker 설정: `Dockerfile`, `docker-compose.yml` — Ubuntu 22.04 기반 이미지에서 Node.js를 설치하고 애플리케이션을 실행합니다.

목표: 스터디 참가자가 다음을 직접 해볼 수 있게 합니다:
- Docker로 컨테이너 빌드/실행
- 브라우저에서 실시간 메시지 교환 테스트
- 간단한 코드 변경(메시지 포맷, UI)→ 재시작→테스트

---

## 요구사항
- Docker 및 Docker Compose가 설치되어 있어야 합니다. (Windows 사용자는 Docker Desktop 권장)
- 기본적인 터미널 사용법(디렉토리 이동, 명령 실행) 숙지

권장 Docker 버전: Docker Engine 20.x 이상

---

## 파일 구조

루트: `6_week/`
- `Dockerfile` — Ubuntu 22.04 기반, Node.js 설치 및 앱 실행
- `docker-compose.yml` — 서비스 구성(포트 포워딩)
- `package.json` — Node 의존성(Express, socket.io)
- `server.js` — 애플리케이션 진입점(웹서버 + Socket.IO)
- `public/index.html` — 클라이언트(채팅 UI)
- `files/` — (빈 디렉토리) 앱에서 사용 가능한 파일 저장소(현재 채팅 예제에선 사용되지 않음)

불필요한 이전 시도 관련 파일(삭제됨): `default.conf`, `nginx.conf`, `upload.html`, 최상위 `index.html` 등

---

## 실행 방법

PowerShell (권장):
```powershell
cd C:\Users\hanmy\doker_study\6_week
docker-compose up --build
```

cmd.exe:
```cmd
cd /d C:\Users\hanmy\doker_study\6_week && docker-compose up --build
```

백그라운드로 실행하려면 `-d` 옵션:
```powershell
docker-compose up --build -d
```

컨테이너 중지/삭제:
```powershell
docker-compose down
```

로그 확인:
```powershell
docker-compose logs -f web
```

이미지 재빌드(소스 변경 후):
```powershell
docker-compose up --build
```

---

## 동작 확인(테스트)

1. 브라우저에서 `http://localhost:8080` 열기
2. 채팅 입력란에 메시지 입력 후 전송
3. 같은 주소를 다른 탭이나 다른 브라우저에서 열어 메시지가 실시간으로 전파되는지 확인

성공 기준: 한 클라이언트에서 보낸 메시지가 모든 연결된 클라이언트의 화면에 거의 즉시 표시됩니다.

---

## 문제 해결(FAQ)

Q: 채팅 메시지가 전송되는지 서버에서 확인하고 싶어요.
A: Docker 컨테이너의 로그를 확인하면 됩니다. 두 가지 방법이 있습니다:
1. 실시간 로그 보기 (권장):
   ```powershell
   docker logs -f 6_week-web-1
   ```
2. 현재까지의 로그 확인:
   ```powershell
   docker logs 6_week-web-1
   ```
정상적으로 작동한다면 다음과 같은 로그를 볼 수 있습니다:
```
Server running on port 3000
client connected [소켓ID]
received message: [사용자가 보낸 메시지]
```

Q: `ERR_CONNECTION_REFUSED` 또는 페이지가 열리지 않아요.
- A1: 컨테이너가 실행 중인지 확인하세요:
  - `docker ps` 출력에서 `6_week-web-1`(또는 비슷한 이름)과 포트 바인딩 `0.0.0.0:8080->3000`을 확인합니다.
  - 컨테이너가 없다면 위의 `docker-compose up --build`를 실행하세요.

Q: `PORT already in use` 에러가 나요.
- A: 호스트의 8080 포트가 이미 사용 중입니다. 사용중인 프로세스를 중지하거나 `docker-compose.yml`에서 다른 포트(예: 8081:3000)로 바꾸세요.

Q: 새 코드를 반영했는데 변경이 보이지 않아요.
- A: `docker-compose up --build`로 재빌드 후 실행하세요. 개발 중에는 컨테이너를 멈추고 재시작하는 대신 파일 바인드를 설정하면 편리하지만, 현재 설정은 이미지 내부에 복사되는 방식입니다.

Q: Socket.IO 연결이 실패합니다.
- A: 브라우저 콘솔(개발자 도구)을 열고 네트워크 탭/콘솔 탭의 에러를 확인하세요. 서버 로그(`docker-compose logs web`)도 함께 확인하면 원인을 빨리 찾을 수 있습니다.

---

## 학습용 확장 과제(권장)
1. 파일 업로드 기능 추가
   - `public`에 업로드 폼을 추가하고 `server.js`에 `multer`를 사용해 `/upload` 엔드포인트를 만들어 파일을 `files/`에 저장하세요.
2. 간단한 인증(닉네임) 추가
   - 접속 시 닉네임을 입력받아 메시지에 닉네임을 포함시키세요.
3. Docker 이미지 최적화
   - 멀티스테이지 빌드를 도입하거나 `node:20-alpine` 기반 이미지를 사용해 이미지 크기를 줄여보세요.
4. HTTPS 적용 테스트
   - 로컬에서 `nginx` 리버스 프록시를 추가하고 `mkcert`로 발급한 로컬 인증서를 사용해 HTTPS 환경을 구성해보세요.

---

## 참고 자료

- [MDN - WebSocket 소개](https://developer.mozilla.org/ko/docs/Web/API/WebSocket)
- [Docker 기초 학습 - Docker Curriculum](https://docker-curriculum.com/)
- [Ubuntu 패키지 관리 - apt 사용법](https://ubuntu.com/server/docs/package-management)

---

