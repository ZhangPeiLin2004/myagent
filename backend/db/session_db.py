


# backend/db/session_db.py
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import os
from sqlalchemy import create_engine
from backend.config import settings
from backend.memory.session_memory import Base

def init_session_database():
    db_path = settings.DB_PATH
    print(f"Try to create session DB at absolute path: {db_path}")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    print(f"✅ Session DB initialized successfully: {db_path}")

if __name__ == "__main__":
    from backend.config import settings
    print("PROJECT_ROOT:", os.path.abspath("."))
    print("Final absolute DB path:", settings.DB_PATH)
    print("DB dir exists:", os.path.exists(os.path.dirname(settings.DB_PATH)))
    init_session_database()
