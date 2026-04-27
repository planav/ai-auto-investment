from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.wallet import Wallet, WalletTransaction, TransactionType, TransactionStatus
from app.schemas.wallet import (
    WalletResponse,
    WalletBalanceResponse,
    TransactionResponse,
    TransactionResponseList,
)


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_wallet(self, user_id: int) -> Wallet:
        """Get or create wallet for user"""
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = result.scalar_one_or_none()

        if not wallet:
            wallet = Wallet(
                user_id=user_id,
                balance=0.0,
                total_deposited=0.0,
                total_withdrawn=0.0,
                total_invested=0.0,
            )
            self.db.add(wallet)
            await self.db.commit()
            await self.db.refresh(wallet)

        return wallet

    async def get_wallet(self, user_id: int) -> Optional[Wallet]:
        """Get wallet for user"""
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_wallet_balance(self, user_id: int) -> WalletBalanceResponse:
        """Get wallet balance"""
        wallet = await self.get_or_create_wallet(user_id)
        return WalletBalanceResponse(
            balance=wallet.balance,
            total_deposited=wallet.total_deposited,
            total_withdrawn=wallet.total_withdrawn,
            total_invested=wallet.total_invested,
            currency=wallet.currency,
        )

    async def deposit(self, user_id: int, amount: float, description: Optional[str] = None) -> WalletResponse:
        """Deposit money to wallet"""
        wallet = await self.get_or_create_wallet(user_id)

        balance_before = wallet.balance
        wallet.balance += amount
        wallet.total_deposited += amount

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            status=TransactionStatus.COMPLETED,
            description=description or "Deposit to investment wallet",
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(wallet)

        return WalletResponse.model_validate(wallet)

    async def withdraw(self, user_id: int, amount: float, description: Optional[str] = None) -> Optional[WalletResponse]:
        """Withdraw money from wallet"""
        wallet = await self.get_or_create_wallet(user_id)

        if wallet.balance < amount:
            return None

        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.total_withdrawn += amount

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.WITHDRAW,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            status=TransactionStatus.COMPLETED,
            description=description or "Withdrawal from investment wallet",
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(wallet)

        return WalletResponse.model_validate(wallet)

    async def deduct_for_investment(self, user_id: int, amount: float, reference_id: str) -> Optional[WalletResponse]:
        """Deduct amount from wallet for investment (creates trade_buy transaction)"""
        wallet = await self.get_or_create_wallet(user_id)

        if wallet.balance < amount:
            return None

        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.total_invested += amount

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.TRADE_BUY,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            status=TransactionStatus.COMPLETED,
            description="Investment in portfolio",
            reference_id=reference_id,
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(wallet)

        return WalletResponse.model_validate(wallet)

    async def refund_investment(self, user_id: int, amount: float, reference_id: str) -> Optional[WalletResponse]:
        """Refund an investment deduction back to wallet (used on portfolio creation failure)."""
        wallet = await self.get_or_create_wallet(user_id)

        balance_before = wallet.balance
        wallet.balance += amount
        wallet.total_invested = max(0.0, (wallet.total_invested or 0) - amount)

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.TRADE_SELL,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            status=TransactionStatus.COMPLETED,
            description="Investment refund — portfolio creation failed",
            reference_id=reference_id,
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(wallet)
        return WalletResponse.model_validate(wallet)

    async def add_from_sale(self, user_id: int, amount: float, reference_id: str, description: str) -> WalletResponse:
        """Add amount to wallet from portfolio sale"""
        wallet = await self.get_or_create_wallet(user_id)

        balance_before = wallet.balance
        wallet.balance += amount

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.TRADE_SELL,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            status=TransactionStatus.COMPLETED,
            description=description,
            reference_id=reference_id,
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(wallet)

        return WalletResponse.model_validate(wallet)

    async def get_transactions(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> TransactionResponseList:
        """Get transaction history"""
        wallet = await self.get_or_create_wallet(user_id)

        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.id)
            .order_by(desc(WalletTransaction.created_at))
            .offset(offset)
            .limit(page_size)
        )
        transactions = result.scalars().all()

        count_result = await self.db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.id)
        )
        total = len(count_result.scalars().all())

        return TransactionResponseList(
            transactions=[TransactionResponse.model_validate(t) for t in transactions],
            total=total,
            page=page,
            page_size=page_size,
        )
