import pytest
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# NOTE: The full DB setup fixtures (setup_db, client, db, lawyer_user) will be added
# in Task 3 (auth) once app/main.py and database.py exist.
# This file is created now so later tasks can import pwd_context from here.
