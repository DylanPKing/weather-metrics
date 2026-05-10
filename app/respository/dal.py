import os
from sqlmodel import create_engine, Session

from dotenv import load_dotenv
from collections.abc import Generator

load_dotenv()

db_url = "postgresql+psycopg://{user}:{password}@{host}/{db}".format(
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ["POSTGRES_HOST"],
    db=os.environ["POSTGRES_DB"],
)

engine = create_engine(db_url)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
