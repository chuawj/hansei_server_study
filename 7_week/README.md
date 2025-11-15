# 🛠 Docker MySQL 컨테이너 실습 (네트워크 생성부터)

## 1. 네트워크 생성
```bash
docker network create db-net
```
- 컨테이너 간 통신을 위한 전용 네트워크 생성

---

## 2. MySQL 컨테이너 실행
```bash
docker run -d --name my-mysql \
  --env MYSQL_ROOT_PASSWORD=MyRoot!234 \
  --env MYSQL_DATABASE=appdb \
  --env MYSQL_USER=appuser \
  --env MYSQL_PASSWORD=AppUser!234 \
  --publish 3307:3306 \
  --volume $PWD/mysql/data:/var/lib/mysql \
  --volume $PWD/mysql/backup:/backup \
  --network db-net \
  mysql:8.0
```
- 루트 비밀번호, 기본 DB, 사용자 계정 설정  
- 데이터와 백업 디렉터리를 호스트에 마운트  
- 포트 3307 사용 (호스트 3306 충돌 방지)

---

## 3. 접속 확인
```bash
docker exec -it my-mysql mysql -uappuser -pAppUser!234 -D appdb -e "SELECT VERSION();"
```
- ✅ **결과**: MySQL 8.0.44 정상 접속 확인

---

## 4. 샘플 데이터 삽입
컨테이너 접속:
```bash
docker exec -it my-mysql mysql -uroot -pMyRoot!234
```

SQL 실행 (setup.sql 파일에 포함):
```sql
USE appdb;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  price DECIMAL(10,2),
  stock INT DEFAULT 0
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  order_date DATE,
  amount DECIMAL(10,2),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  product_id INT,
  quantity INT,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO users (name, email) VALUES
('Kim', 'kim@example.com'),
('Lee', 'lee@example.com'),
('Park', 'park@example.com');

INSERT INTO products (name, price, stock) VALUES
('Laptop', 1200.00, 10),
('Mouse', 25.00, 100),
('Keyboard', 45.00, 50);

INSERT INTO orders (user_id, order_date, amount) VALUES
(1, '2025-11-01', 1225.00),
(2, '2025-11-02', 45.00);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 1),
(2, 3, 1);
```

---

## 5. 데이터 확인
```bash
docker exec -it my-mysql mysql -uroot -pMyRoot!234 -e "SELECT * FROM appdb.users;"
```

**✅ 실행 결과**:
```
+----+------+------------------+---------------------+
| id | name | email            | created_at          |
+----+------+------------------+---------------------+
|  1 | Kim  | kim@example.com  | 2025-11-15 07:26:11 |
|  2 | Lee  | lee@example.com  | 2025-11-15 07:26:11 |
|  3 | Park | park@example.com | 2025-11-15 07:26:11 |
+----+------+------------------+---------------------+
```

---

## 6. 백업 생성

### 전체 DB 백업
```bash
docker exec my-mysql sh -c \
  'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --all-databases --single-transaction' \
  > ./mysql/backup/all_$(date +%F_%H%M).sql
```

### 특정 DB 백업
```bash
docker exec my-mysql sh -c \
  'exec mysqldump -uroot -p"MyRoot!234" appdb --single-transaction' \
  > ./mysql/backup/appdb_$(date +%F_%H%M).sql
```

**✅ 백업 파일 생성 완료**:
- `appdb_2025-11-15_1626.sql` (9992 bytes)
- `appdb_2025-11-15_1628.sql` (9992 bytes)

---

## 7. 파일 이동 (컨테이너 ↔ 호스트)

### 컨테이너 → 호스트
```bash
docker cp my-mysql:/tmp/all.sql ./mysql/backup/all.sql
```

### 호스트 → 컨테이너
```bash
docker cp ./mysql/backup/appdb.sql my-mysql:/tmp/appdb.sql
```

---

## 8. 복구 실행
```bash
docker exec -i my-mysql mysql -uroot -pMyRoot!234 appdb < ./mysql/backup/appdb_2025-11-15_1626.sql
```

---

## 9. 파일 삭제

### 컨테이너 내부 파일 삭제
```bash
docker exec my-mysql rm /tmp/appdb.sql
```

### 호스트 백업 파일 삭제
```bash
rm ./mysql/backup/appdb.sql
```

---

## 10. 자동화 (Windows Task Scheduler 예시)

매일 새벽 3시에 전체 백업 (cron 불가, Task Scheduler 사용):
```powershell
# PowerShell 스크립트로 자동 백업 설정
$date = Get-Date -Format "yyyy-MM-dd_HHmm"
docker exec my-mysql mysqldump -uroot -pMyRoot!234 --all-databases > "C:\backup\all_$date.sql"
```

---


### 🚀 주요 포트 정보
- **MySQL**: 3307 (호스트) → 3306 (컨테이너)
- **네트워크**: db-net (컨테이너 간 통신용)
- **컨테이너 이름**: my-mysql

---

## 📝 실습 참고 사항

### MySQL 접속 방법
```powershell
# 컨테이너 내부 접속
docker exec -it my-mysql mysql -uroot -pMyRoot!234

# 특정 데이터베이스 접속
docker exec -it my-mysql mysql -uappuser -pAppUser!234 -D appdb
```

### 자주 사용하는 명령어
```powershell
# 컨테이너 상태 확인
docker ps -a | findstr my-mysql

# 컨테이너 로그 확인
docker logs my-mysql

# 컨테이너 종료
docker stop my-mysql

# 컨테이너 재시작
docker start my-mysql

# 컨테이너 완전 삭제 (데이터 폴더는 유지)
docker rm my-mysql
```

---

## 환경설정 & 데이터베이스 사용법 (상세)

### 1) 사전 요구사항
- Docker 엔진 설치: Docker Desktop (Windows) 권장
- Docker Compose 사용 가능(Compose V2 권장)
- PowerShell 사용 시 경로 처리 주의 (예시에서는 `$PWD` 대신 `(Get-Location).Path` 사용)

설치 확인:
```powershell
docker --version
docker compose version
```

### 2) 폴더 권한 및 볼륨 준비
- 데이터 영속성을 위해 호스트에 디렉토리를 생성합니다:
```powershell
mkdir -Force .\7_week\mysql\data
mkdir -Force .\7_week\mysql\backup
```
- Windows에서 Docker 볼륨 바인드 시 권한 문제가 발생하면 관리자 권한으로 Docker Desktop을 실행하거나 볼륨 경로를 WSL2의 리눅스 경로로 옮겨 사용하세요.

### 3) 컨테이너 실행(권장 명령 — PowerShell용)
```powershell
$PWD_PATH = (Get-Location).Path
docker run -d --name my-mysql `
  --env MYSQL_ROOT_PASSWORD=MyRoot!234 `
  --env MYSQL_DATABASE=appdb `
  --env MYSQL_USER=appuser `
  --env MYSQL_PASSWORD=AppUser!234 `
  --publish 3307:3306 `
  --volume "$PWD_PATH\7_week\mysql\data:/var/lib/mysql" `
  --volume "$PWD_PATH\7_week\mysql\backup:/backup" `
  --network db-net `
  mysql:8.0
```

포인트:
- 호스트 포트(예:3307)는 이미 사용 중일 수 있으니 `docker ps`로 확인 후 변경하세요.
- 컨테이너가 처음 시작될 때 DB 초기화(사용자/데이터베이스 생성)에 시간이 걸릴 수 있습니다.

### 4) MySQL 접속 및 기본 사용
- 컨테이너 내부에서 루트로 접속:
```powershell
docker exec -it my-mysql mysql -uroot -pMyRoot!234
```
- 호스트에서 MySQL 클라이언트로 접속:
```powershell
# 로컬 MySQL 클라이언트가 설치된 경우
mysql -h 127.0.0.1 -P 3307 -uappuser -pAppUser!234 -D appdb
```

기본 쿼리 예제:
```sql
-- DB 목록 보기
SHOW DATABASES;

-- 테이블 생성 (예시: users)
CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50));

-- 데이터 삽입
INSERT INTO users (name) VALUES ('Kim');

-- 조회
SELECT * FROM users;
```

### 5) 백업 및 복구
- 전체 DB 백업 (호스트에 파일 저장 — PowerShell 예시)
```powershell
$date = Get-Date -Format "yyyy-MM-dd_HHmm"
docker exec my-mysql sh -c 'exec mysqldump -uroot -p"MyRoot!234" --all-databases --single-transaction' > "${PWD}\7_week\mysql\backup\all_$date.sql"
```

- 특정 DB 백업
```powershell
docker exec my-mysql sh -c 'exec mysqldump -uroot -p"MyRoot!234" appdb --single-transaction' > "${PWD}\7_week\mysql\backup\appdb_$date.sql"
```

- 복구 (호스트의 백업 파일을 컨테이너에 투입하여 실행)
```powershell
docker exec -i my-mysql mysql -uroot -pMyRoot!234 appdb < .\7_week\mysql\backup\appdb_2025-11-15_1634.sql
```

팁:
- 비밀번호를 커맨드라인에 직접 노출하는 것은 보안상 바람직하지 않습니다. 테스트 후 스크립트나 환경에서 직접 노출을 줄이세요.

### 6) 문제 해결(자주 발생하는 문제)
- 포트 충돌: `docker ps`로 어떤 컨테이너가 포트를 점유하는지 확인 후 중지(`docker stop <id>`) 또는 호스트 포트 변경
- 권한 문제: 호스트와 컨테이너 간 볼륨 권한 문제는 관리자 권한 실행 또는 WSL 경로 사용으로 해결
- 백업 실패(권한 부족): `mysqldump`를 루트 사용자로 실행하거나 적절한 권한을 부여

---

## 추가 권장 사항 및 체크리스트 (실습 성공률을 높이기 위한 항목)

아래 항목들을 확인해두면 실습 중 발생할 수 있는 문제를 빠르게 해결할 수 있습니다.

- 1) MySQL 클라이언트 설치(선택)
  - 호스트에서 직접 `mysql` CLI로 접속하려면 로컬에 MySQL 클라이언트가 필요합니다.
  - Windows: `choco install mysql` 또는 `winget install MySQL.MySQLServer` 등으로 설치 가능.

- 2) 포트 사용 확인 (문제가 발생하면 우선 확인)
  - Windows PowerShell:
    ```powershell
    netstat -ano | findstr ":3307"    # 호스트 포트 사용 여부 확인
    docker ps -a                         # 어떤 컨테이너가 실행 중인지 확인
    ```

- 3) 컨테이너 로그 확인
  - 컨테이너 내부 에러/초기화 상태는 `docker logs`로 확인합니다:
    ```powershell
    docker logs my-mysql
    ```

- 4) 백업 권한 이슈
  - `mysqldump` 실행 시 appuser로 권한 부족(PROCESS 등) 오류가 발생할 수 있습니다. 이 경우:
    - 루트로 백업 실행 (권장): `mysqldump -uroot -p"MyRoot!234" ...`
    - 또는 필요 시 DB 사용자에 `PROCESS` 권한 부여 (루트로 접속하여 실행):
      ```sql
      GRANT PROCESS ON *.* TO 'appuser'@'%';
      FLUSH PRIVILEGES;
      ```

- 5) 백업/복구 검증
  - 백업 파일이 생성되면 파일 크기(`Get-ChildItem`)와 파일 시작 부분(`head`)으로 SQL 헤더가 있는지 확인하세요.
  - 복구 테스트는 별도 테스트 DB(또는 임시 컨테이너)를 사용해 복원이 정상 동작하는지 검증하십시오.

- 6) 데이터 영속성 주의
  - 호스트 폴더를 직접 바인드하면 Windows 권한/소유자 이슈가 발생할 수 있습니다. 장기 실습 시에는 Docker Named Volume 사용도 고려하세요:
    ```powershell
    docker volume create mysql-data
    docker run -v mysql-data:/var/lib/mysql ...
    ```

- 7) 클린업(정리) 권장 명령
  - 컨테이너 정리:
    ```powershell
    docker stop my-mysql
    docker rm my-mysql
    # (필요 시) 백업 폴더 정리
    Remove-Item -Recurse -Force .\7_week\mysql\data\*
    ```

- 8) Docker Compose 예시(선호 시)
  - `docker run` 대신 `docker-compose.yml`로 관리하면 편리합니다. 예시:
    ```yaml
    version: '3.8'
    services:
      mysql:
        image: mysql:8.0
        container_name: my-mysql
        environment:
          MYSQL_ROOT_PASSWORD: MyRoot!234
          MYSQL_DATABASE: appdb
          MYSQL_USER: appuser
          MYSQL_PASSWORD: AppUser!234
        ports:
          - "3307:3306"
        volumes:
          - ./mysql/data:/var/lib/mysql
          - ./mysql/backup:/backup
        networks:
          - db-net

    networks:
      db-net:
        external: true
    ```

---

필요하면 위의 `docker-compose.yml` 예시를 실제 파일로 만들어 드리거나, `SETUP.md`로 분리해서 실습 절차를 더 단계별로 정리해 드리겠습니다.



