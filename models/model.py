from pydantic import BaseModel
from datetime import datetime


class WalletUpdateRequest(BaseModel):
    amount: float


class HistoryTransactionResponse(BaseModel):
    transaction_id: int
    wallet_id: int
    transaction_type: str
    amount: float
    timestamp: datetime