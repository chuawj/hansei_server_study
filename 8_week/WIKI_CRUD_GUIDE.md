# CRUD 실습 가이드 — 상세한 로직 설명 (8_week 기준)

요청: "지금 로직이 어떻게 동작하는지, CRUD가 코드에서 어떻게 구현되어 있는지 쉽게 자세히 설명해 달라"는 내용에 맞춰 문서를 정리합니다.

대상 파일
- `8_week/main.py`  — 백엔드 핵심 로직
- `8_week/static/index.html` — 프론트엔드(브라우저) 로직

목표
- 코드 흐름을 순서대로 읽어 이해할 수 있게 설명
- 각 엔드포인트가 내부에서 어떤 작업을 하는지(DB 흐름 포함) 예시와 함께 제공
- 프론트엔드와의 주고받는 데이터(요청/응답 예시) 제공

---

## 1) 전체 구조(한 문장)
FastAPI(`main.py`)가 HTTP 엔드포인트를 제공하고, SQLAlchemy를 통해 MySQL에 `Tip` 레코드를 생성/조회/수정/삭제하며, 브라우저(`index.html`)는 fetch()로 해당 엔드포인트를 호출해 화면을 갱신합니다.

---

## 2) `main.py` 로직 상세

1) 초기화(가장 위 부분)
- 환경변수 `DATABASE_URL`을 읽어 SQLAlchemy 엔진을 생성합니다.
- `SessionLocal`은 DB 세션(factory)입니다. 실제 요청에서는 `get_db()`로 세션을 얻어 사용합니다.
- `Base = declarative_base()`로 모델의 베이스 클래스를 만듭니다.

코드 포인트:
```python
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://appuser:AppUser!234@mysql:3306/appdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(...)
Base = declarative_base()
```

설명: `engine`은 DB 연결 정보를 가지고 있으며, `SessionLocal()`로 생성한 세션(`db`)으로 쿼리를 수행합니다.

2) 모델 정의 (`Tip`)
- `Tip` 클래스는 `tips` 테이블을 나타냅니다.
- 주요 컬럼: `id`(PK), `title`, `content`, `author`, `created_at`(생성 시간 자동 입력)

코드 포인트:
```python
class Tip(Base):
    __tablename__ = "tips"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    content = Column(String(2000))
    author = Column(String(100), default="anonymous")
    created_at = Column(DateTime, default=datetime.utcnow)
```

설명: `index=True`는 검색 성능을 위해 인덱스를 생성하는 힌트입니다. `default=datetime.utcnow`로 생성 시각을 자동 입력합니다.

3) Pydantic 스키마
- `TipCreate`는 클라이언트가 보내는 요청(제목/내용/작성자)을 검증합니다.
- `TipResponse`는 DB 모델을 응답 형태로 반환할 때 사용하는 스키마입니다. `Config.from_attributes=True`로 SQLAlchemy 객체를 Pydantic으로 바로 변환할 수 있습니다.

4) DB 세션 의존성
- `get_db()` 제너레이터는 요청마다 DB 세션을 열고( yield ) 처리가 끝나면 닫습니다.

코드 포인트:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

설명: FastAPI의 `Depends(get_db)`로 각 엔드포인트에 주입되며, 세션 누수를 방지합니다.

5) 정적 파일 제공
- `app.mount("/static", StaticFiles(...))`로 `static/` 폴더를 서빙하고, 루트(`/`)에서는 `FileResponse`로 `index.html`을 반환합니다.

6) `startup` 이벤트
- `Base.metadata.create_all(bind=engine)`를 호출해 테이블이 없으면 생성합니다. (개발용 자동 생성)

7) CRUD 엔드포인트 동작

- Create (POST `/tips/`)
  - 입력: JSON `{title, content, author}`
  - 동작: `db_tip = Tip(...)` 생성 → `db.add()` → `db.commit()` → `db.refresh(db_tip)` → 생성된 객체 반환
  - 핵심: `commit()`으로 DB에 반영하고, `refresh()`로 자동 생성된 `id`와 `created_at`을 다시 로드합니다.

  요청 예시:
  ```json
  {"title": "간단한 팁", "content": "내용", "author": "lee"}
  ```

  응답 예시:
  ```json
  {"id": 5, "title": "간단한 팁", "content": "내용", "author": "lee", "created_at": "2025-11-29T13:00:00"}
  ```

- Read list (GET `/tips/`)
  - 입력: 쿼리 파라미터 `skip`, `limit` 기본값이 있음
  - 동작: `db.query(Tip).order_by(Tip.created_at.desc()).offset(skip).limit(limit).all()`
  - 응답: Tip 객체 배열(JSON)

- Read one (GET `/tips/{tip_id}`)
  - 동작: `filter(Tip.id == tip_id).first()`로 조회, 없으면 `HTTPException(404)` 반환

- Update (PUT `/tips/{tip_id}`)
  - 입력: JSON `{title, content, author}`
  - 동작: 먼저 해당 레코드 조회 → 존재하지 않으면 404 → 필드 업데이트 → `db.commit()` → `db.refresh()` → 반환
  - 주의: 이 구현은 전체 필드를 대체하는 방식입니다(부분 업데이트는 별도 구현 필요).

- Delete (DELETE `/tips/{tip_id}`)
  - 동작: 조회 → 없으면 404 → `db.delete(db_tip)` → `db.commit()` → 성공 메시지 반환

---

## 3) `index.html`(프론트엔드) 로직 상세

1) API_BASE
- `const API_BASE = "http://localhost:8000"`로 백엔드 주소를 하드코딩합니다. (개발용)

2) 주요 함수 흐름
- `createTip()`
  - 입력값 검사(빈값 차단)
  - `fetch(POST /tips/)`로 JSON 전송
  - 성공 시 입력 초기화 및 `loadTips()` 호출

- `loadTips()`
  - `fetch(GET /tips/)` 호출 → JSON 파싱 → `window.tipsCache`에 저장
  - DOM을 동적으로 생성해 목록 렌더링

- `editTip(id)` / `saveTip(id)` / `cancelEditTip(id)`
  - 편집 UI로 전환 → 저장 시 `PUT /tips/{id}` 호출 → 목록 갱신

- `deleteTip(id)`
  - 확인창 → `DELETE /tips/{id}` 호출 → 목록 갱신

3) XSS 방지
- `escapeHtml()`로 사용자 입력을 HTML 이스케이프하여 DOM에 직접 주입할 때 스크립트 실행을 방지합니다. (프론트엔드 측 방어)

4) 클라이언트 상태
- `window.tipsCache`는 현재 로드된 팁 배열을 메모리에 보관해 편집 취소 시 원래 값을 복원합니다.

---

## 4) 요청/응답 예시 (요약)

- POST /tips/ 요청
  - Body: `{"title":"A","content":"B","author":"C"}`
  - 응답: 생성된 팁 객체 (id 포함)

- GET /tips/
  - 응답: `[{id:.., title:.., content:.., author:.., created_at:..}, ...]`

- PUT /tips/{id}
  - Body: `{"title":"X","content":"Y","author":"Z"}`
  - 응답: 수정된 객체

- DELETE /tips/{id}
  - 응답: `{ "message": "팁 #N이 삭제되었습니다" }`

---

### 4-1) 실제 curl 실행 예시와 예상 응답 (샘플)

아래 예시는 로컬에서 `docker-compose`로 앱을 띄운 후 PowerShell 또는 터미널에서 실행할 수 있는 샘플입니다. 응답은 개발 환경의 상태에 따라 달라질 수 있으나, 일반적으로 아래와 같은 JSON 형태를 기대합니다.

- Create (POST /tips/)
```bash
curl -s -X POST "http://localhost:8000/tips/" \
  -H "Content-Type: application/json" \
  -d '{"title":"테스트 팁","content":"테스트 내용","author":"tester"}'
```
예상 출력 (stdout):
```json
{
  "id": 12,
  "title": "테스트 팁",
  "content": "테스트 내용",
  "author": "tester",
  "created_at": "2025-11-29T14:30:00"
}
```

- Read all (GET /tips/)
```bash
curl -s http://localhost:8000/tips/
```
예상 출력:
```json
[
  {
    "id": 12,
    "title": "테스트 팁",
    "content": "테스트 내용",
    "author": "tester",
    "created_at": "2025-11-29T14:30:00"
  },
  {
    "id": 11,
    "title": "다른 팁",
    "content": "내용",
    "author": "lee",
    "created_at": "2025-11-29T13:00:00"
  }
]
```

- Read one (GET /tips/1)
```bash
curl -s http://localhost:8000/tips/12
```
예상 출력:
```json
{
  "id": 12,
  "title": "테스트 팁",
  "content": "테스트 내용",
  "author": "tester",
  "created_at": "2025-11-29T14:30:00"
}
```

- Update (PUT /tips/1)
```bash
curl -s -X PUT "http://localhost:8000/tips/12" \
  -H "Content-Type: application/json" \
  -d '{"title":"수정된 제목","content":"수정된 내용","author":"tester"}'
```
예상 출력:
```json
{
  "id": 12,
  "title": "수정된 제목",
  "content": "수정된 내용",
  "author": "tester",
  "created_at": "2025-11-29T14:30:00"
}
```

- Delete (DELETE /tips/1)
```bash
curl -s -X DELETE http://localhost:8000/tips/12
```
예상 출력:
```json
{"message":"팁 #12이 삭제되었습니다"}
```


## 5) 트랜잭션/일관성/주의사항

- 각 엔드포인트는 `db.commit()`을 호출해 변경을 영구화합니다. 실패 시 예외가 발생하면 트랜잭션이 롤백됩니다(기본 SQLAlchemy 행동).
- `update` 구현은 전체 필드를 다시 덮어씌우므로 부분 업데이트(patch)가 필요하면 추가 구현 필요.
- 대량 동시성(복수 사용자가 동시에 수정)에는 낙관적/비관적 잠금 전략이 필요합니다(현재 구현에는 없음).

---

## 6) 디버깅 포인트(실제 문제 발생 시 우선 확인 순서)

1. 컨테이너 상태 확인:
```powershell
docker-compose ps
```

2. FastAPI 로그 확인:
```powershell
docker-compose logs fastapi-app --tail=200
```

3. MySQL 로그 확인:
```powershell
docker-compose logs mysql --tail=200
```

4. DB 직접 확인:
```powershell
docker-compose exec mysql mysql -u appuser -p appdb
# SELECT * FROM tips;
```

5. 네트워크/포트 문제: 브라우저에서 `http://localhost:8000` 대신 컨테이너 내부 호스트명(`http://fastapi-app:8000`)을 사용하면 안 됩니다 — 브라우저는 로컬 호스트로 접근해야 함.

---

## 7) 보안/운영 참고

- 운영 환경에서는 DB 비밀번호와 민감 정보를 환경변수(Secrets)로 관리하세요.
- 사용자 입력은 서버에서도 유효성 검증을 추가하세요(길이, 필수 항목, 허용 문자 등).
- CORS: 현재 예제는 로컬에서 동일 호스트로 동작하도록 되어 있음. 다른 도메인에서 접근하려면 CORS 설정 필요.

---

## 8) 간단 체크리스트(테스트 항목)

- [ ] POST로 팁 생성 가능
- [ ] GET 목록이 최신순으로 반환되는지 확인
- [ ] PUT으로 수정 후 값이 반영되는지 확인
- [ ] DELETE로 삭제 후 더 이상 조회되지 않는지 확인
- [ ] 브라우저에서 편집/취소 흐름이 정상 동작하는지 확인

---

필요하시면 이 문서를 팀 위키 마크업(Confluence)으로 변환하거나, 엔드포인트별 예제 요청/응답을 더 추가해 드리겠습니다.


