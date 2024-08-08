from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional, Union, List
from datetime import datetime

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
    investment_advice: List[str] = []
    images_url: Optional[List[str]] = []

class StructuredMessage(BaseModel):
    headline: Optional[str] = None
    subtitle: Optional[str] = None
    rest_message: Optional[str] = None

class EmailBody(BaseModel):
    receiver_email: EmailStr
    subject: str
    type: Literal["normal", "advise", "recommendation", "alert", "notification"] = "normal"
    message: Union[SimpleMessage, StructuredMessage, RecommendationMessage] = RecommendationMessage

class IssueProblem(BaseModel):
    error_type: Literal["bug", "mistake", "missing", "other"] = "bug"
    description: Optional[str] = None

class TokenSchema(BaseModel):
    token: str
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]
    universe_domain: str
    account: str
    expiry: Optional[datetime] = None

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

