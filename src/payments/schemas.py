from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
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
        return str(bal)


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
        return str(amo)


class PaymentOutSchemas(PaymentBaseSchemas):
    transaction_id: UUID4 = Field(default_factory=uuid4)

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("transaction_id")
    def serialize_id(self, tra: UUID4, _info):
        return str(tra)


class PaymentGenerateBaseSchemas(BaseModel):
    transaction_id: str = Field(default="")
    account_id: int
    user_id: int
    amount: Decimal

    @field_serializer("amount")
    def serialize_balance(self, amo: Decimal, _info):
        return str(amo)


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
        return str(amo)
