import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

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
