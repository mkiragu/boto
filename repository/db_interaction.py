from repository.db_models import User, Category, Transaction, Wallet
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from dto.transaction_dto import TransactionType
from dto.wallet_dto import Currency
from exceptions.resource_not_found import ResourceNotFoundException


def get_user(user_id: str, db: Session):
    user = get_user_info(user_id, db)

    if user is None:
        raise ResourceNotFoundException()
    
    return user

def get_user_info(user_id: str, db: Session):
    return db.query(User).get(user_id)

def add_user_locally(user: User, db: Session):
    db.add(user)
    db.commit()
    db.refresh(user)

def add_wallet_locally(wallet: Wallet, db: Session):
    db.add(wallet)
    db.commit()
    db.refresh(wallet)

def add_category_locally(category: Category, db: Session):
    db.add(category)
    db.commit()
    db.refresh(category)

def add_transaction_locally(transaction: Transaction, db: Session):
    db.add(transaction)
    db.commit()

def get_wallet(user_id: str, db: Session):

    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if wallet is None:
        raise ResourceNotFoundException()
    return wallet

def get_all_user_transactions(page: int, page_size: int, auth_user_id: str, category_id: str, db: Session):
    offset = (page - 1) * page_size
    # Create a query to filter transactions based on user_id and optional category_id
    query = db.query(Transaction).join(Category).filter(Category.user_id == auth_user_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    # Apply pagination and return list of transactions
    return query.offset(offset).limit(page_size).all()

def get_all_user_categories(page: int, page_size: int, auth_user_id: str, db: Session):
    offset = (page - 1) * page_size
    # Apply pagination and return list of categories
    return db.query(Category).filter(Category.user_id == auth_user_id).offset(offset).limit(page_size).all()

def calculate_wallet_changes(auth_user_id: str, amount_decimal: Decimal, transaction_type: str, db: Session):
    user = get_user(auth_user_id, db)
    user_wallet = {}

    if user.wallets:
        user_wallet = user.wallets[0]
    else:
        user_wallet = Wallet(
            uid=str(uuid.uuid4()),
            user_id=auth_user_id,
            balance=amount_decimal,
            currency=Currency.USD  # Set the default currency
        )
        db.add(user_wallet)
        db.commit()

    if transaction_type == TransactionType.INCOME.name:
        user_wallet.balance += amount_decimal
    elif transaction_type == TransactionType.EXPENSE.name:
        user_wallet.balance -= amount_decimal
    
    db.commit()