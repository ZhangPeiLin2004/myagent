


# session_memory

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import tiktoken
import os
from backend.config import settings

Base = declarative_base()
engine = create_engine(f"sqlite:///{os.path.abspath(settings.DB_PATH)}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM Tables
class SessionRecord(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageRecord(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SessionMemoryManager:
    def __init__(self):
        self.db = SessionLocal()
        self.enc = tiktoken.get_encoding("cl100k_base")
        self.max_token_limit = int(settings.MAX_HISTORY_TOKENS)

    def create_session(self, name: str) -> int:
        rec = SessionRecord(name=name)
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec.id

    def list_sessions(self):
        return self.db.query(SessionRecord).all()

    def add_message(self, session_id: int, role: str, content: str):
        msg = MessageRecord(session_id=session_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()

    def get_messages(self, session_id: int):
        msgs = self.db.query(MessageRecord).filter(MessageRecord.session_id == session_id).order_by(MessageRecord.created_at).all()
        raw = [{"role": m.role, "content": m.content} for m in msgs]
        return self._truncate_by_token(raw)

    def _truncate_by_token(self, msg_list):
        total = 0
        res = []
        for m in reversed(msg_list):
            cnt = len(self.enc.encode(m["content"]))
            if total + cnt > self.max_token_limit:
                break
            total += cnt
            res.insert(0, m)
        return res

    def close(self):
        self.db.close()

