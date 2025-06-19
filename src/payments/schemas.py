from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    UUID4,
)


class ScoreBaseSchemas(BaseModel):
    account_number: str
    balance: Decimal = Field(max_digits=15, decimal_places=2)
    date_creation: datetime

    @field_serializer("date_creation")
    def serialize_date_of_issue(self, dt: datetime, _info):
        return dt.strftime("%d-%b-%Y")

    @field_serializer("balance")
    def serialize_balance(self, bal: Decimal, _info):
        return float(bal)


class ScoreOutSchemas(ScoreBaseSchemas):
    account_id: int

    model_config = ConfigDict(from_attributes=True)


class PaymentBaseSchemas(BaseModel):
    amount: Decimal = Field(max_digits=15, decimal_places=2)
    date_creation: datetime

    @field_serializer("date_creation")
    def serialize_date_creation(self, dt: datetime, _info):
        return dt.strftime("%d-%b-%Y")

    @field_serializer("amount")
    def serialize_balance(self, amo: Decimal, _info):
        return float(amo)


class PaymentOutSchemas(PaymentBaseSchemas):
    transaction_id: UUID4 = Field(default_factory=uuid4)

    model_config = ConfigDict(from_attributes=True)


class PaymentGenerateBaseSchemas(BaseModel):
    transaction_id: str = Field(default="")
    account_id: int
    user_id: int
    amount: Decimal

    @field_serializer("amount")
    def serialize_balance(self, amo: Decimal, _info):
        return float(amo)


class PaymentGenerateOutSchemas(PaymentGenerateBaseSchemas):
    signature: str


class TransactionInSchemas(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    signature: str

    @field_serializer("amount")
    def serialize_balance(self, amo: Decimal, _info):
        return float(amo)
