import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from alembic.config import Config
from sqlalchemy import ForeignKey, Integer, String, Text, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from alembic import command


def uid():
    return str(uuid4())


def now():
    return datetime.now(UTC).isoformat()


class Base(DeclarativeBase):
    pass


class Record(Base):
    __tablename__ = "records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    payload: Mapped[str] = mapped_column(Text)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("records.id"), index=True)
    stage: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30))


class Store:
    def __init__(self, url):
        opts = {"check_same_thread": False} if url.startswith("sqlite") else {}
        self.engine = create_engine(
            url, connect_args=opts, **({"poolclass": StaticPool} if ":memory:" in url else {})
        )
        if url.startswith("sqlite"):

            @event.listens_for(self.engine, "connect")
            def enable_foreign_keys(connection, record):
                connection.execute("PRAGMA foreign_keys=ON")

        cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        with self.engine.begin() as connection:
            cfg.attributes["connection"] = connection
            command.upgrade(cfg, "head")
        self.factory = sessionmaker(self.engine)

    def put(self, kind, data):
        with self.factory.begin() as s:
            s.merge(Record(id=data["id"], kind=kind, payload=json.dumps(data, ensure_ascii=False)))

    def get(self, kind, key):
        with self.factory() as s:
            row = s.get(Record, key)
            return json.loads(row.payload) if row and row.kind == kind else None

    def all(self, kind):
        with self.factory() as s:
            return [json.loads(r.payload) for r in s.scalars(select(Record).where(Record.kind == kind))][::-1]

    def event(self, data, stage, status="running"):
        data.update(stage=stage, status=status)
        self.put("session", data)
        with self.factory.begin() as s:
            s.add(Event(session_id=data["id"], stage=stage, status=status))

    def events(self, key, after=0):
        with self.factory() as s:
            return [
                {"id": r.id, "stage": r.stage, "status": r.status}
                for r in s.scalars(
                    select(Event).where(Event.session_id == key, Event.id > after).order_by(Event.id)
                )
            ]
