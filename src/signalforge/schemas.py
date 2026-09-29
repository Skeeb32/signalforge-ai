from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Nonnegative = Annotated[float, Field(ge=0, le=1e9, allow_inf_nan=False)]


class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    call_failures: Nonnegative | None
    complaints: Literal[0, 1] | None
    tenure: Nonnegative | None
    charge_band: Annotated[float, Field(ge=0, le=9, allow_inf_nan=False)] | None
    seconds_of_use: Nonnegative | None
    call_count: Nonnegative | None
    sms_count: Nonnegative | None
    distinct_contacts: Nonnegative | None
    tariff_plan: Literal[1, 2] | None
    age: Annotated[float, Field(ge=0, le=120, allow_inf_nan=False)] | None


class Batch(BaseModel):
    customers: list[Customer] = Field(min_length=1, max_length=500)


class Feedback(BaseModel):
    prediction_id: int = Field(gt=0)
    label: Literal[0, 1]
