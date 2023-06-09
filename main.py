from typing import List
import logging

from fastapi.exceptions import RequestValidationError, ValidationError
from fastapi import FastAPI, status, Response, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from datetime import datetime

from schemas.schemas import AccountCreate, WalletCreate, HistoryTransactionResponse, WalletUpdateRequest
from config.database import Account, Wallet, HistoryTransaction, engine

app = FastAPI()
# session = Session(engine)
security = HTTPBasic()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    with Session(engine) as session:
        query = session.query(Account).filter(Account.email == credentials.username)
        account = query.first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        if account.password != credentials.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        return account


def get_wallet(wallet_id: int, authenticated: Account = Depends(authenticate)):
    with Session(engine) as session:
        wallet = session.query(Wallet).filter(Wallet.wallet_id == wallet_id).filter(Wallet.account_id == authenticated.account_id).first()
        if not wallet:
            logger.error("Wallet not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        return wallet


@app.post("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    account = authenticate(credentials)
    return {"message": "Login successful", "account_id": account.account_id}


@app.post("/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountCreate, response: Response):
    with Session(engine) as session:
        email = session.query(Account).filter(Account.email == account.email).first()
        if email is None:
            db_user = Account(email=account.email, password=account.password, username=account.username)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            logger.info("create account completed successfully")
            return db_user
        else:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            logger.error("Account creation failed. Email may not exist or duplicate account entry")
            session.rollback()
            return {"error": "Account creation failed. Email may not exist or duplicate account entry."}


@app.post("/wallets", status_code=status.HTTP_201_CREATED)
async def create_wallet(wallet: WalletCreate, response: Response, authenticated: Account = Depends(authenticate)):
    with Session(engine) as session:
        exist_wallet = session.query(Wallet).filter(Wallet.account_id == authenticated.account_id).first()
        if exist_wallet is None:
            db_wallet = Wallet(balance=wallet.balance, account_id=authenticated.account_id)
            session.add(db_wallet)
            session.commit()
            session.refresh(db_wallet)
            logger.info("create wallet completed successfully")
            return db_wallet

        else:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            logger.error("Wallet creation failed. Account ID may not exist or duplicate wallet entry.")
            session.rollback()
            return {"error": "Wallet creation failed. Account ID may not exist or duplicate wallet entry."}


@app.put("/wallets/deposite", status_code=status.HTTP_200_OK)
async def deposite(wallet_update: WalletUpdateRequest, response: Response, wallet: Wallet = Depends(get_wallet)):
    with Session(engine) as session:
        # wallet = session.get(Wallet, wallet.wallet_id)
        if not wallet:
            response.status_code = status.HTTP_404_NOT_FOUND
            logger.error("Wallet not found")
            return {"error": "Wallet not found"}

        wallet.balance += wallet_update.amount

        history_transaction = HistoryTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="deposit",
            amount=wallet_update.amount,
            timestamp=datetime.now()
        )

    session.add(history_transaction)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    logger.info(f"deposit {wallet_update.amount} completed successfully for wallet id : {wallet.wallet_id}")
    return wallet


@app.put("/wallets/withdraw", status_code=status.HTTP_200_OK)
async def withdraw(wallet_update: WalletUpdateRequest, response: Response, wallet: Wallet = Depends(get_wallet)):
    with Session(engine) as session:
        # wallet = session.get(Wallet, wallet_id)
        if not wallet:
            response.status_code = status.HTTP_404_NOT_FOUND
            logger.error("Wallet not found")
            return {"error": "Wallet not found"}

        if wallet.balance < wallet_update.amount:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            logger.error("Insufficient balance")
            return {"error": "Insufficient balance"}

        wallet.balance -= wallet_update.amount

        history_transaction = HistoryTransaction(
            wallet_id=wallet.wallet_id,
            transaction_type="withdraw",
            amount=wallet_update.amount,
            timestamp=datetime.now()
        )

    session.add(history_transaction)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)
    logger.info(f"Withdraw {wallet_update.amount} completed successfully for wallet id : {wallet.wallet_id}")

    return wallet


@app.get("/wallets/{wallet_id}/history")
async def get_wallet_history(wallet: Wallet = Depends(get_wallet)) -> List[HistoryTransactionResponse]:
    with Session(engine) as session:
        transactions = session.query(HistoryTransaction).filter(HistoryTransaction.wallet_id == wallet.wallet_id).all()
        logger.info(f"History translation completed successfully for wallet id : {wallet.wallet_id}")
        return transactions


@app.get("/wallets/{source_wallet_id}/transfer/{destination_wallet_id}/{amount}", status_code=status.HTTP_200_OK)
async def transfer_money(destination_wallet_id: int, amount: float, response: Response, source_wallet: Wallet = Depends(get_wallet)):
    try:
        with Session(engine) as session:
            source_wallet = session.get(Wallet, source_wallet.wallet_id)
            destination_wallet = session.get(Wallet, destination_wallet_id)

            if not source_wallet or not destination_wallet:
                response.status_code = status.HTTP_404_NOT_FOUND
                logger.error("Wallet not found")
                return {"error": "Wallet not found"}

            if source_wallet.balance < amount:
                response.status_code = status.HTTP_406_NOT_ACCEPTABLE
                logger.error("Insufficient balance")
                return {"error": "Insufficient balance"}

            source_wallet.balance -= amount
            destination_wallet.balance += amount

            # Save the changes in the wallets
            session.add(source_wallet)
            session.add(destination_wallet)

            # history transaction records
            source_transaction = HistoryTransaction(
                wallet_id=source_wallet.wallet_id,
                transaction_type="withdraw",
                amount=amount,
                timestamp=datetime.now()
            )
            destination_transaction = HistoryTransaction(
                wallet_id=destination_wallet_id,
                transaction_type="deposit",
                amount=amount,
                timestamp=datetime.now()
            )
            session.add(source_transaction)
            session.add(destination_transaction)
            session.commit()
            logger.info(
                f"Transfer of {amount} from wallet {source_wallet.wallet_id} to wallet {destination_wallet_id} completed "
                f"successfully")

            return {"message": "Money transferred successfully"}

    # When a validation error in the request body
    except RequestValidationError as validation_error:
        raise HTTPException(status_code=422, detail=validation_error.errors())

    # When failed validation rules
    except ValidationError as validation_error:
        error_msg = validation_error.errors()[0]["msg"]
        raise HTTPException(status_code=400, detail=error_msg)

    except IntegrityError as e:
        logger.error(f"Transfer failed: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Transfer failed")
