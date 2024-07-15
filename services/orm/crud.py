from .database import async_engine
from .models import *
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import asyncio

# USER WHOLE CRUD

async def create_new_user(username, password, email, client_ip):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            try:
                new_user_conf = {
                    # Add configuration details here
                }

                new_user = User(
                    username=username,
                    password=password,
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
              

async def delete_user(user_id: str):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            user_to_delete = await session.get(User, user_id)
            session.delete(user_to_delete)

            await session.flush()

            return {"status": "sucess"}


async def update_user(user_id: str, new_username: str = None, new_email: str = None):
    pass

async def get_user(user_id: str):
    async with AsyncSession(async_engine) as session:
        async with session.begin():

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
    await create_new_user("mrpau", "123456", "XXXXXXXXXXXXXXX", "127.0.0.1")

if __name__ == "__main__":
    asyncio.run(main_proofs())