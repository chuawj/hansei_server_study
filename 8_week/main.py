from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import os
from pathlib import Path

# ========== 설정 ==========
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://appuser:AppUser!234@mysql:3306/appdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI 앱 초기화
app = FastAPI(title="팁 커뮤니티 - Tip Community", version="1.0")

# ========== DB 모델 (SQLAlchemy) ==========
# Tip model: 커뮤니티 팁/게시글
class Tip(Base):
    __tablename__ = "tips"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    content = Column(String(2000))
    author = Column(String(100), default="anonymous")
    created_at = Column(DateTime, default=datetime.utcnow)

# ========== Pydantic 스키마 ==========
class TipCreate(BaseModel):
    title: str
    content: str
    author: str | None = "anonymous"

class TipResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime

    class Config:
        from_attributes = True

# ========== DB 의존성 ==========
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== API 엔드포인트 ==========

# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 대시보드 (HTML 페이지)
@app.get("/")
def dashboard():
    """팁 커뮤니티 대시보드 페이지"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return {"error": "static/index.html not found"}

@app.get("/health")
def health_check():
    """헬스 체크"""
    return {"status": "healthy"}

# ========== 앱 시작 이벤트 ==========
@app.on_event("startup")
def startup():
    """서버 시작 시 DB 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created!")

# ========== Tips API (커뮤니티 게시글) ==========
@app.post("/tips/", response_model=TipResponse)
def create_tip(tip: TipCreate, db: Session = Depends(get_db)):
    """새로운 팁 작성"""
    db_tip = Tip(title=tip.title, content=tip.content, author=tip.author or "anonymous")
    db.add(db_tip)
    db.commit()
    db.refresh(db_tip)
    return db_tip

@app.get("/tips/", response_model=list[TipResponse])
def list_tips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 팁 조회 (최신순)"""
    tips = db.query(Tip).order_by(Tip.created_at.desc()).offset(skip).limit(limit).all()
    return tips

@app.get("/tips/{tip_id}", response_model=TipResponse)
def get_tip(tip_id: int, db: Session = Depends(get_db)):
    """특정 팁 조회"""
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="팁을 찾을 수 없습니다")
    return tip

@app.put("/tips/{tip_id}", response_model=TipResponse)
def update_tip(tip_id: int, tip: TipCreate, db: Session = Depends(get_db)):
    """팁 수정"""
    db_tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not db_tip:
        raise HTTPException(status_code=404, detail="팁을 찾을 수 없습니다")
    db_tip.title = tip.title
    db_tip.content = tip.content
    db_tip.author = tip.author or db_tip.author
    db.commit()
    db.refresh(db_tip)
    return db_tip

@app.delete("/tips/{tip_id}")
def delete_tip(tip_id: int, db: Session = Depends(get_db)):
    """팁 삭제"""
    db_tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not db_tip:
        raise HTTPException(status_code=404, detail="팁을 찾을 수 없습니다")
    db.delete(db_tip)
    db.commit()
    return {"message": f"팁 #{tip_id}이 삭제되었습니다"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
