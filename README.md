# Wallet API

This is a simple API for managing wallets and performing deposit and withdrawal transactions. It is built with FastAPI and uses SQLModel as the ORM for interacting with the database.

## Prerequisites

- Python 3.8 or higher
- Pip package manager

## Installation

1. Clone the repository:

```bash
   git clone https://github.com/zahra395/WalletAPI
```

Navigate to the project directory:
```bash
cd wallet-api
```

Install the dependencies:
```bash
    pip3 install -r requirements.txt
```

## Configuration

1. Open the main.py file and update the database_url variable with your desired database connection URL.
2. You can further customize the database connection by modifying the create_engine parameters in main.py.

## Usage

1. Start the server:
```bash
    uvicorn main:app --reload
```

2. The API will be accessible at http://localhost:8000.

3. Use a tool like cURL, Postman, or a web browser to interact with the API endpoints.

## API Endpoints
### Deposit Amount

- Endpoint: /wallets/{wallet_id}/deposit
- Method: PUT
- Request Body:
```json
{
  "amount": 100.0
}
```
Response:

```json
    {
      "wallet_id": 1,
      "account_id": 1,
      "balance": 150.0
    }
```

### Withdraw Amount

- Endpoint: /wallets/{wallet_id}/withdraw
- Method: PUT
- Request Body:

```json
{
  "amount": 50.0
}
```
Response:

```json
    {
      "wallet_id": 1,
      "account_id": 1,
      "balance": 100.0
    }
```
### Get Wallet History

- Endpoint: /wallets/{wallet_id}/history
- Method: GET
- Response:
```json
    [
      {
        "transaction_id": 1,
        "wallet_id": 1,
        "transaction_type": "deposit",
        "amount": 100.0,
        "timestamp": "2023-05-21T10:30:00"
      },
      {
        "transaction_id": 2,
        "wallet_id": 1,
        "transaction_type": "withdraw",
        "amount": 50.0,
        "timestamp": "2023-05-21T11:30:00"
      }
    ]
```