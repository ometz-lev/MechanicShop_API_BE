from dotenv import load_dotenv
import os
import sys
from sqlalchemy import create_engine, text

load_dotenv()
uri = os.getenv('SQLALCHEMY_DATABASE_URI')
print('URI =', uri)

if not uri:
    print('No SQLALCHEMY_DATABASE_URI found in environment')
    sys.exit(1)

engine = create_engine(uri)
with engine.begin() as conn:
    table_result = conn.execute(text("SHOW TABLES LIKE 'customers'"))
    if table_result.fetchone() is None:
        print('customers table does not exist; nothing to migrate')
        sys.exit(0)

    columns = conn.execute(text('SHOW COLUMNS FROM customers')).fetchall()
    column_names = [column[0] for column in columns]
    print('Current columns =', column_names)

    if 'password' not in column_names:
        conn.execute(text('ALTER TABLE customers ADD COLUMN password VARCHAR(100) NOT NULL'))
        print('ADDED_PASSWORD_COLUMN')
    else:
        print('PASSWORD_COLUMN_ALREADY_EXISTS')
