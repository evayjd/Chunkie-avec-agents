from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# Session 工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# ORM Base
Base = declarative_base()


# --------------------------------------------------
# 初始化数据库（创建表）
# --------------------------------------------------

def init_db():
    """
    创建所有 ORM 定义的表
    """
    import backend.db.models  # 确保 models 被加载
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FastAPI 依赖
# --------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()