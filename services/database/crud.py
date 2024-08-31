from .database import async_engine
from .models import *
from sqlalchemy import select, update, insert, delete
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
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
                    return {"status": "error", "error": "DB connection in the server does not work, maybe the container is not running"}
                except Exception as e:
                    print("An error occurred:", e)
                    raise
    return wrapper

# USER WHOLE CRUD

@db_connection
async def create_new_user(session: AsyncSession, username: str, password: str, email: str, country: str, client_ip: str):
    try:
        new_user_conf = {
                "cvi": {},
                "economic_calendar": {}
            }

        new_user = User(
                username=username,
                password=password,
                country=country,
                email=email,
                configuration=new_user_conf,
                session_ips=[client_ip]  # Initialize session_ips as a list of strings
            )
        session.add(new_user)
        await session.flush()

        # Manually query the new user's ID before committing the transaction
        user_id_query = await session.execute(select(User.id).where(User.email == email))
        user_id = user_id_query.scalar()

        await session.commit()

        return {
            "status": "success",
            "user_data": {
                "user_id": user_id,
                "username": username,
                "email": email
            }
        }

    except IntegrityError as e:
                await session.rollback()
                if "UNIQUE constraint failed: user.username" in str(e):
                    return {"status": "error", "error": "Username already exists"}
                elif "UNIQUE constraint failed: user.email" in str(e):
                    return {"status": "error", "error": "Email already exists"}
                else:
                    return {"status": "error", "error": f"An error ocurred: {e}"}

              

@db_connection
async def logout_user(session: AsyncSession, user_id: str, user_ip: str):
    """Logout user, just remove the IP"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # Remove the IP
    user_ips = list(user.session_ips)
    if user_id in user_ips:
        user_ips.remove(user_ip)

        # Update result in the db
        await session.execute(
            update(User).
            where(User.id == user_id).
            values(session_ips=user_ips)
        )
        return True
    else:
        return None
    

async def update_user(user_id: str, new_username: str = None, new_email: str = None):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            pass

@db_connection
async def login_user(session: AsyncSession, username: str, password: str, client_ip: str):
        try:
            result = await session.execute(select(User).where(User.username == username, User.password == password))

            user = result.scalar_one_or_none()
            if user:
                print(user.id)

                # If user, add new session ips
                if user:
                    user_ips = user.session_ips if user.session_ips else []
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
                    "status": "success",
                    "user_data": {
                        "user_id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "configuration": user.configuration
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": "User does not exsit in the database"
                }
        except OSError:
            return {
                "status": "error",
                "error": "An error occurred while logging in the user"
            }
        
@db_connection
async def get_user(session: AsyncSession, user_id: str):
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        selected_user = result.scalar_one_or_none()
        
        return {
            "status": "success",
            "user_data": {
                "user_id": selected_user.id,
                "username": selected_user.username,
                "email": selected_user.email,
                "configuration": dict(selected_user.configuration)
            }
        }
    except DBAPIError:
        return {
            "status": "error",
            "error": f"User id {user_id} does not exsit in the database"
        }
    
async def get_user_email(email: str):
    async with AsyncSession(async_engine) as session:
        async with session.begin():

            selected_user = await session.execute(select(User).where(User.email == email))
            user = selected_user.scalar_one()

            return user


@db_connection
async def delete_user(session: AsyncSession, user_id: str):
    # Modify this over the time!
    try:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user:
            await session.delete(user)
            await session.flush()
            return {
                "status": "success",
                "message": f"user {user_id} was successfully deleted"
            }
        else:
            return {
                "status": "error",
                "message": f"User {user_id} does not exist in the database"
            }
    except DBAPIError:
        return {
            "status": "error",
            "message": f"User {user_id} does not exist in the database"
        }

@db_connection
async def add_new_error(session: AsyncSession, subject: str, text: str):
    """Add new error log"""
    new_error = ErrorsLogs(subject=subject, text=text)
    session.add(new_error)
    await session.flush()


async def main_proofs():
    # Create new user proff
    # await create_new_user("mrpau", "123456", "XXXXXXXXXXXXXXX", "BR", "127.0.0.1")
    result = await add_new_error("error log subject", "error log large")
    print(result)

if __name__ == "__main__":
    asyncio.run(main_proofs())