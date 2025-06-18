from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


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
