from sqlmodel import SQLModel, create_engine, Field
# from sqlmodel import
from datetime import datetime

from setting import AppSettings

settings = AppSettings()
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)


class Account(SQLModel, table=True):
    account_id: int = Field(default=None, primary_key=True, )
    username: str = Field(max_length=50)
    email: str = Field(index=True, unique=True)
    password: str = Field()


class Wallet(SQLModel, table=True):
    wallet_id: int = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.account_id", unique=True)
    balance: float


class HistoryTransaction(SQLModel, table=True):
    transaction_id: int = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="wallet.wallet_id")
    transaction_type: str
    amount: float
    timestamp: datetime = Field(default_factory=datetime.now)


SQLModel.metadata.create_all(engine)
