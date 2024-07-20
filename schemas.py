from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional, Union, List

class Order(BaseModel):
    symbol: str
    mode: Literal["short", "long"]
    amount_usdt: Optional[int] = None
    price: Optional[str] = None
    leverage: Optional[int] = 5

class Fear_greedSubscribe(BaseModel):
    email_sender: str
    user_id: str
    notification_level: Literal[1,2,3] = 1

class Fear_greedUnSubscribe(BaseModel):
    user_id: str


class Options_totalAmount(BaseModel):
    coin: Optional[str] = "USDT"
    assetType: Literal["all", "hold_only"] = "all"

class CloseOrder(BaseModel):
    price: Optional[float] = None

class SimpleMessage(BaseModel):
    message: str

class RecommendationMessage(BaseModel):
    crypto_name: str
    headline: str
    subtitle: str
    details: str
    investment_advice: List[str]

class StructuredMessage(BaseModel):
    headline: Optional[str] = None
    subtitle: Optional[str] = None
    rest_message: Optional[str] = None

class EmailBody(BaseModel):
    receiver_email: EmailStr
    subject: str
    type: Literal["normal", "advise", "recommendation", "alert", "notification"] = "normal"
    message: Union[SimpleMessage, StructuredMessage, RecommendationMessage] = StructuredMessage

# USER SCHEMA
class UserBase(BaseModel):
    username: str

class RegisterUser(UserBase):
    email: EmailStr
    password: str
    country: str

class LoginUser(UserBase):
    password: str 


# SUBSCRIPTIONS

