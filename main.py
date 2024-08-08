from fastapi import FastAPI, Security, HTTPException, status, Depends, Request
from fastapi.security import APIKeyHeader
from services.bitget import BitgetClient
from services.schedule_taks.email_sender import EmailSender
from services.database import crud
from services import schemas
from typing import Literal, Optional
import uvicorn, asyncio, json, datetime
import schedule

# Clients
app = FastAPI(title="Bitget Pau's API")
bitget_client = BitgetClient()
email_sender = EmailSender(
    token_path='/home/ubuntu/Bitget_API/bitget_proxy_api/schedule_taks/credentials/emailtoken.json',
    creds_path='/home/ubuntu/Bitget_API/bitget_proxy_api/schedule_taks/credentials/credentials.json',
    sender_email='devtravel36o@gmail.com'
)

api_key_header = APIKeyHeader(name="password")

def get_user(api_key_header: str = Security(api_key_header)):
    if api_key_header == "mierda69":
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key"
    )

# SCHEMAS
# Ensure that schemas module is properly imported and has the required schema definitions

# ENDPOINTS
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/get_positions", tags=["Trading"])
async def get_possitions():
    return dict(await bitget_client.get_positions())

@app.get("/assets", description="Get Account Assets including total assets, available balance, unrealized PnL, ROI, and used margin", tags=["Trading"])
async def get_assets(): 
    # Get positions and future assets
    positions = await bitget_client.get_positions()
    future_assets_ps = await bitget_client.get_future_possitions()

    # Get Unrealized pnl
    unrealized_pnl = sum(float(tot['unrealizedPL']) for tot in positions['data']) 

    # Get total USDT used
    usdt_used = sum(float(tot['marginSize']) for tot in positions['data'])
    
    # Total Account Future Assets
    total_assets = float(future_assets_ps['data'][0]['usdtEquity'])

    # Calculate ROI correctly
    initial_margin = total_assets - unrealized_pnl
    if initial_margin != 0:
        roi = (unrealized_pnl / initial_margin) * 100
    else:
        roi = 0

    # Available
    available = total_assets - usdt_used

    return {
        "account_assets": round(total_assets, 2),
        "available": round(available, 2),
        "total_unrealized_PnL": round(unrealized_pnl, 2),
        "ROI": f"{round(roi, 2)}%",
        "Used": round(usdt_used, 2)
    }


@app.get("/get_futures_historical_orders", tags=["Trading"])
async def historial_orders():
    # Get historial orders
    historial_orders_ = await bitget_client.get_historial_orders() 
    return historial_orders_['data']

@app.get("/get_last_order", tags=["Trading"])
async def last_order():
    historial_orders_ = await bitget_client.get_historial_orders() 
    last_order = historial_orders_['data']['entrustedList']

    return last_order

@app.post("/open_order_futures_normal", description="Place Order without stoploss and auto calculated leverage", tags=["Trading"])
async def open_order(request_boddy: schemas.Order, user: bool = Depends(get_user)):
    # Set leverage as x5 if provided and as needed
    if str.lower(request_boddy.symbol) == 'btc':
        laverage = 20
        await bitget_client.set_leverage(request_boddy.symbol, str(request_boddy.leverage) if request_boddy.leverage else laverage)
    elif str.lower(request_boddy.symbol) == 'eth':
        laverage = 10
        await bitget_client.set_leverage(request_boddy.symbol, str(request_boddy.leverage) if request_boddy.leverage else laverage)
    else:
        laverage = 5
        await bitget_client.set_leverage(request_boddy.symbol, str(request_boddy.leverage) if request_boddy.leverage else laverage)

    # Calculate amount of crypto
    if not request_boddy.amount_usdt:
        # Get total assets
        future_assets_ps = await bitget_client.get_future_positions()
        positions = await bitget_client.get_positions()
        total_assets = float(future_assets_ps['data'][0]['usdtEquity'])
        usdt_used = sum(float(tot['marginSize']) for tot in positions['data'])

        # Calculate Amountlaverage
        if total_assets > 500:
            if str.lower(request_boddy.symbol) == 'btc':
                amount_percentage = 0.17 if total_assets < 1000 else 0.14
            elif str.lower(request_boddy.symbol) == 'eth':
                amount_percentage = 0.15 if total_assets < 1000 else 0.12
            else:
                amount_percentage = 0.17 if total_assets < 1000 else 0.14
            amount_usdt = (total_assets - usdt_used) * amount_percentage
        else:
            amount_usdt = total_assets * 0.1  # Fallback to 10% of total assets if less than $500

        # Get crypto valuee
        asset_price = await bitget_client.get_crypto_price(request_boddy.symbol)
        amount = (amount_usdt / float(asset_price)) * laverage
    else:
        asset_price = await bitget_client.get_crypto_price(request_boddy.symbol)
        amount = (float(request_boddy.amount_usdt) / float(asset_price)) * laverage

    # Place order
    place_order = asyncio.create_task(bitget_client.open_order_futures(
        symbol=request_boddy.symbol,
        amount=amount,
        mode="Sell" if request_boddy.mode == "long" else "Sell",
        price=request_boddy.price
    ))
    await place_order

    return {"response": "Order placed"}

@app.post("/close_order/{symbol}", tags=["Trading"])
async def close_order(symbol, request_boddy:schemas.CloseOrder, user: bool = Depends(get_user)):
    return dict(await bitget_client.close_order(symbol))

@app.post("/send_email", tags=["Other Services"])
async def send_email(request_boddy: schemas.EmailBody):

    if isinstance(request_boddy.message, schemas.SimpleMessage):
        if len(request_boddy.message.message) < 50:
            message_body = {"headline": request_boddy.message.message, "subtitle": "", "rest_message": ""}
        elif len(request_boddy.message.message) < 200:
            message_body = {"headline": "", "subtitle": request_boddy.message.message, "rest_message": ""}
        else:
            message_body = {"headline": "", "subtitle": "", "rest_message": request_boddy.message.message}

    elif isinstance(request_boddy.message, schemas.StructuredMessage):
        message_body = {"headline": request_boddy.message.headline, "subtitle": request_boddy.message.subtitle, "rest_message": request_boddy.message.rest_message}

    if request_boddy.type == "advise":
        email_sender.advise_email(
            receiver_email=request_boddy.receiver_email,
            subject=request_boddy.subject,
            message=message_body
        )
    elif request_boddy.type == "normal":
        email_sender.normal_email(
            receiver_email=request_boddy.receiver_email,
            subject=request_boddy.subject,
            content=request_boddy.message.message
        )
    elif request_boddy.type == "notification":
        pass
    elif request_boddy.type == "alert":
        pass
    elif request_boddy.type == "recommendation":
        message_body = {
            "crypto_name": request_boddy.message.crypto_name,
            "headline": request_boddy.message.headline,
            "subtitle": request_boddy.message.subtitle,
            "details": request_boddy.message.details,
            "investment_advice": request_boddy.message.investment_advice,
            "image_url": request_boddy.message.images_url
        }

        await email_sender.recommendation_email(
            receiver_email=request_boddy.receiver_email,
            subject=request_boddy.subject,
            recommendation=message_body
        )
    return {"status":"success", "response": "Email has been sent!"}

@app.post("/notificate_node_issue", tags=["Other Services"], description="Report an issue to the developer. An email will be sended")
async def notificate_issue_to_developer(request_boddy: schemas.IssueProblem):
    
    today = datetime.datetime.today()
    subject = f"New error type {request_boddy.error_type} the day {today.strftime("%d/%m/%Y")} at {today.strftime("%H:%M")}"

    # Send email to notify the error
    asyncio.create_task(email_sender.error_email(subject=subject, message=request_boddy.description))

    # Add Error Log into the db
    result = await crud.add_new_error(subject=subject, text=request_boddy.description)

    return {"status":"success", "message": "The error has been notificated!"}

@app.post("/renew_email_token", description="Renew email token", tags=["Other Services"])
async def renew_email_token(request_body: schemas.TokenSchema, user: bool = Depends(get_user)):
    new_email_token = request_body.model_dump()

    # Save email
    with open('services/schedule_taks/credentials/emailtoken.json', 'w') as file:
        json.dump(new_email_token, file)

    return {"result": "success", "response": "new token has been updated successfully"}

@app.post("/fear_and_greed/subscribe", tags=["Subscriptions"])
async def fear_greed_note(request_boddy: schemas.Fear_greedSubscribe, user: bool = Depends(get_user)):

    # Send request to subscribe to pasive node

    return {"response": "under construction"}

@app.post("/fear_and_greed/unsubscribe", tags=["Subscriptions"])
async def fear_greed_note(request_boddy: schemas.Fear_greedUnSubscribe, user: bool = Depends(get_user)):

    # Send request to subscribe to pasive node

    return {"response": "under construction"}

@app.post("/economic_calendar/subscribe", tags=["Subscriptions"])
async def subscribe_to_economic_calendar(user: bool = Depends(get_user)):
    return {"response": "under construction"}

@app.post("/economic_calendar/unsubscribe", tags=["Subscriptions"])
async def unsubscribe_to_economic_calendar(user: bool = Depends(get_user)):
    return {"response": "under construction"}

# USER SESSION

@app.post("/register_user", tags=["User Session"])
async def register_user(request: Request, request_boddy: schemas.RegisterUser):
    client_ip = request.client.host
    # Create new user in the database
    result = await crud.create_new_user(
        username=request_boddy.username, 
        password=request_boddy.password, 
        email=request_boddy.email,
        country=request_boddy.country,
        client_ip=client_ip
    )

    return result


@app.post("/login_user", tags=["User Session"])
async def login_user(request: Request, request_boddy: schemas.LoginUser):
    client_ip = request.client.host
    result = await crud.login_user(
        username=request_boddy.username,
        password=request_boddy.password,
        client_ip=client_ip
    )

    return result

@app.post("/user_session/{user_id}", tags=["User Session"])
async def logout_user(user_id: str):
    """Send user session as well as its username, email and subscribed modules"""
    user_session = await crud.get_user(user_id)

    return user_session

@app.put("/logout/{user_id}", tags=["User Session"])
async def logout_user(request: Request, user_id: str):
    """End user session"""
    cliet_ip = request.client.host
    response = await crud.logout_user(user_id, cliet_ip)
    if response:
        return {"status":"sucess", "response": "User logout properly"}
    else:
        return {"status": "sucess", "response": "The ip does not exist in the db, so nothing has happenedd"}

@app.delete("/delete_user/{user_id}", tags=["User Session"])
async def delete_user_permanently(user_id):
    "Remove and all its data from the db"
    response = await crud.delete_user(user_id)

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
