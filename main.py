from fastapi import FastAPI
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

allow_all = ['*']
app.add_middleware(
   CORSMiddleware,
   allow_origins=allow_all,
   allow_credentials=True,
   allow_methods=allow_all,
   allow_headers=allow_all
)

from routers import (
    auth_api,
    categories_api,
    transactions_api,
    users_api,
    wallets_api
)

# Adding API routes 👇
app.include_router(auth_api.router, prefix="/api/v1/auth")
app.include_router(users_api.router, prefix="/api/v1/users")
app.include_router(categories_api.router, prefix="/api/v1/categories")
app.include_router(transactions_api.router, prefix="/api/v1/transactions")
app.include_router(wallets_api.router, prefix="/api/v1/wallets")
