from pydantic import BaseModel


# Define Pydantic schema
class AccountCreate(BaseModel):
    username: str
    email: str
    password: str


class WalletCreate(BaseModel):
    account_id: int
    balance: float


class WalletUpdateRequest(BaseModel):
    amount: float


class HistoryTransactionResponse(BaseModel):
    transaction_id: int
    wallet_id: int
    transaction_type: str
    amount: float
