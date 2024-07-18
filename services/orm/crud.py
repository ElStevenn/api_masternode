from .database import async_engine
from .models import *
from sqlalchemy import select, update, insert, delete
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import asyncio


def db_connection(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                try:                
                    result = await func(session, *args, **kwargs)
    
                    return result
                except OSError:
                    return {"status": "error", "error": "DB connection in the server does not work"}
                except Exception as e:
                    print("An error occurred:", e)
                    raise
    return wrapper

# USER WHOLE CRUD

@db_connection
async def create_new_user(session: AsyncSession, username, password, email, country, client_ip):
            try:
                new_user_conf = {
                    # Add configuration details here
                }

                new_user = User(
                    username=username,
                    password=password,
                    country=country,
                    email=email,
                    configuration=new_user_conf,
                    session_ips=f'[{client_ip}]'
                )
                session.add(new_user)
                await session.flush()

                return {
                    "status":"sucess",
                    "user_data": {
                        "user_id": new_user.id,
                        "username": new_user.username,
                        "email": new_user.email
                    }
                }
            
            except IntegrityError as e:
                await session.rollback()
                if "UNIQUE constraint failed: user.username" in str(e):
                    return {"status": "error", "error": "Username already exists"}
                elif "UNIQUE constraint failed: user.email" in str(e):
                    return {"status": "error", "error": "Email already exists"}
                else:
                    return {"status": "error", "error": "An error occurred while creating the user"}
              

@db_connection
async def logout_user(session: AsyncSession, user_id: str, user_ip: str):
    """Logout user, just remove the IP"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # Remove the IP
    user_ips = list(user.session_ips)
    user_ips.remove(user_ip)

    # Update result in the db
    await session.execute(
        update(User).
        where(User.id == user_id).
        values(session_ips=user_ips)
    )

    



async def update_user(user_id: str, new_username: str = None, new_email: str = None):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            pass

@db_connection
async def login_user(session: AsyncSession, username: str, password: str, client_ip: str):
            try:
                result = await session.execute(select(User).where(User.username == username, User.password == password))

                user = result.scalar_one_or_none()
                print(user.id)

                # If user, add new session ips
                if user:
                    user_ips = list(user.session_ips)
                    if client_ip not in user_ips:
                        user_ips.append(client_ip)
                    
                    stmt = (
                        update(User).
                        where(User.id == user.id).
                        values(session_ips=user_ips)
                    )

                    await session.execute(stmt)
                    await session.flush()

                # Add new operations here if needed

                return {
                    "status":"sucess",
                    "user_data":{
                        "user_id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "configuration": user.configuration
                    }
                }
            except OSError:
                return {
                    "status": "error",
                    "error": "An error occurred while logging in the user"
                }
            
@db_connection
async def get_user(session: AsyncSession, user_id: str):
            selected_user = await session.get(User, user_id)
            return selected_user

async def get_user_email(email: str):
    async with AsyncSession(async_engine) as session:
        async with session.begin():

            selected_user = await session.execute(select(User).where(User.email == email))
            user = selected_user.scalar_one()

            return user


async def main_proofs():
    # Create new user proff
    # await create_new_user("mrpau", "123456", "XXXXXXXXXXXXXXX", "BR", "127.0.0.1")
    result = await login_user("mrpau", "123456", "127.0.0.1")
    print(result)

if __name__ == "__main__":
    asyncio.run(main_proofs())