from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy import insert, select

# Create engine and metadata
engine = create_engine("postgresql+psycopg2://postgres:mierda69@localhost:5432/Crypto_Collection")
metadata = MetaData()

# Define the email_list table
email_list_table = Table(
    'email_list', metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String))

# Create the table in the database
metadata.create_all(engine)

def add_new_email(email: str):
    with engine.connect() as conn:
        stmt = insert(email_list_table).values(email=email)
        conn.execute(stmt)
        conn.commit()

def get_all_emails():
    with engine.connect() as conn:
        stmt = select([email_list_table.c.email])
        result = conn.execute(stmt)
        emails = [row[0] for row in result.fetchall()]
        return emails

# Example usage
if __name__ == "__main__":
    # Add a new email
    add_new_email("example@example.com")

    # Get all emails
    emails = get_all_emails()
    print(emails)
