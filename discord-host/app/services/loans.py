from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from shared.database.models import AuditLog, Loan, LoanPayment
from shared.database.session import SessionLocal


class LoanService:
    def __init__(self) -> None:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured")

    def request(self, user_id: str, amount: Decimal, installments: int, idempotency_key: str):
        if amount <= 0 or amount > Decimal("50000"):
            raise ValueError("Amount must be positive and cannot exceed 50.000")
        if not 1 <= installments <= 12:
            raise ValueError("Installments must be between 1 and 12")
        with SessionLocal() as session:
            existing = session.execute(select(Loan).where(Loan.idempotency_key == idempotency_key)).scalar_one_or_none()
            if existing:
                return existing
            loan = Loan(idempotency_key=idempotency_key, user_id=user_id, requested_amount=amount, interest_rate=Decimal("0.25"), installments=installments, status="pending")
            session.add(loan)
            session.commit()
            session.refresh(loan)
            return loan

    def approve(self, administrator_id: str, loan_id: int, approved_amount: Decimal | None):
        with SessionLocal() as session:
            loan = session.get(Loan, loan_id)
            if loan is None:
                raise LookupError("Loan not found")
            if loan.status != "pending":
                raise ValueError("Loan is not pending")
            if approved_amount is None:
                approved_amount = Decimal(str(loan.requested_amount))
            if approved_amount <= 0 or approved_amount > Decimal("50000"):
                raise ValueError("Approved amount must be positive and cannot exceed 50.000")
            week_start = datetime.utcnow() - timedelta(days=7)
            approved = session.execute(select(Loan).where(Loan.status == "approved", Loan.created_at >= week_start)).scalars().all()
            weekly_total = sum((Decimal(str(item.approved_amount or 0)) for item in approved), Decimal("0"))
            if weekly_total + approved_amount > Decimal("50000"):
                raise ValueError("Weekly approved loan limit exceeded")
            loan.approved_amount = approved_amount
            loan.status = "approved"
            due_at = datetime.utcnow()
            total = (approved_amount * Decimal("1.25")).quantize(Decimal("0.01"))
            base_installment = (total / loan.installments).quantize(Decimal("0.01"), rounding="ROUND_DOWN")
            allocated = Decimal("0")
            for number in range(1, loan.installments + 1):
                due_at += timedelta(days=7)
                amount = base_installment
                if number == loan.installments:
                    amount = total - allocated
                else:
                    allocated += amount
                session.add(LoanPayment(loan_id=loan.id, installment_number=number, amount=amount, due_at=due_at))
            loan.due_at = due_at
            session.add(AuditLog(administrator_id=administrator_id, action="approve_loan", entity_type="loan", entity_id=str(loan.id), before_value={"status": "pending", "requested": str(loan.requested_amount)}, after_value={"status": "approved", "approved": str(approved_amount), "total_with_interest": str(total)}, reason="Manual loan approval"))
            session.commit()
            session.refresh(loan)
            return loan

    def reject(self, administrator_id: str, loan_id: int, reason: str):
        if not reason.strip():
            raise ValueError("A reason is required")
        with SessionLocal() as session:
            loan = session.get(Loan, loan_id)
            if loan is None:
                raise LookupError("Loan not found")
            if loan.status != "pending":
                raise ValueError("Loan is not pending")
            loan.status = "rejected"
            session.add(AuditLog(administrator_id=administrator_id, action="reject_loan", entity_type="loan", entity_id=str(loan.id), before_value={"status": "pending"}, after_value={"status": "rejected"}, reason=reason.strip()))
            session.commit()

    def pay(self, loan_id: int, installment_number: int):
        with SessionLocal() as session:
            payment = session.execute(select(LoanPayment).where(LoanPayment.loan_id == loan_id, LoanPayment.installment_number == installment_number).with_for_update()).scalar_one_or_none()
            if payment is None:
                raise LookupError("Installment not found")
            if payment.paid_at is not None:
                return payment
            loan = session.get(Loan, loan_id)
            if loan is None or loan.status != "approved":
                raise ValueError("Loan is not approved")
            from shared.database.models import GlobalBalance, EconomyTransaction
            balance = session.execute(select(GlobalBalance).where(GlobalBalance.user_id == loan.user_id).with_for_update()).scalar_one_or_none()
            amount = Decimal(str(payment.amount))
            before = Decimal(str(balance.balance)) if balance else Decimal("0")
            if before < amount:
                raise ValueError("Insufficient global balance")
            if balance is None:
                raise ValueError("Global balance not found")
            balance.balance = before - amount
            payment.paid_at = datetime.utcnow()
            remaining = session.execute(select(LoanPayment).where(LoanPayment.loan_id == loan_id, LoanPayment.paid_at == None)).scalars().all()
            if not remaining:
                loan.status = "paid"
            idempotency = f"loan-payment:{loan_id}:{installment_number}"
            existing = session.execute(select(EconomyTransaction).where(EconomyTransaction.idempotency_key == idempotency)).scalar_one_or_none()
            if existing is None:
                session.add(EconomyTransaction(idempotency_key=idempotency, user_id=loan.user_id, guild_id=None, kind="loan_payment", amount=amount, balance_before=before, balance_after=before - amount, reason="Loan installment payment"))
            session.commit()
            session.refresh(payment)
            return payment
