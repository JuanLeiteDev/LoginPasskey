from app.database.db import SessionLocal

def get_session():
    session = SessionLocal()

    try:
        with session.begin():
            yield session
    finally:
        session.close()
