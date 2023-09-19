from myApp import db, bcrypt
from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    """Define the structure of the "User" object used in the flask app.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    first_name = Column(Text)
    last_name = Column(Text)
    email = Column(Text, unique=True)
    creation_datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_modified_datetime = Column(DateTime(timezone=True), server_default=func.now())
    creation_userid = Column(Text, nullable=False, server_default='system')
    last_modified_userid = Column(Text, server_default='system')
    sso = Column(Text, unique=False)

    def __init__(self, *args, **kwargs) -> None:
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.sso = kwargs.get("sso") if kwargs.get("sso") else None
        self.first_name = kwargs.get("first_name") if kwargs.get("first_name") else None
        self.last_name = kwargs.get("last_name") if kwargs.get("last_name") else None
        self.email = kwargs.get("email") if kwargs.get("email") else None

    def __repr__(self) -> str:
        return f"<User {self.id}>:(" \
               f"username=\"{self.username}\"" \
               f", first_name=\"{self.first_name}\"" \
               f", last_name=\"{self.last_name}\"" \
               f", email=\"{self.email}\"" \
               f", creation_date=\"{self.creation_datetime}\"" \
               f", creation_user=\"{self.creation_userid}\"" \
               f", modified_date=\"{self.last_modified_datetime}\"" \
               f", modified_user=\"{self.last_modified_userid}\"" \
               f", sso=\"{self.sso})\""

    def set_empty_properties(self) -> None:
        if self.first_name is None:
            self.first_name = ""
        if self.last_name is None:
            self.last_name = ""
        if self.email is None:
            self.email = ""

    def clear_empty_properties(self) -> None:
        if len(self.first_name.strip()) == 0:
            self.first_name = None
        if len(self.last_name.strip()) == 0:
            self.last_name = None
        if len(self.email.strip()) == 0:
            self.email = None

    @staticmethod
    def get_formatted_date(date) -> str:
        if date is None:
            return ""
        return date.strftime("%B %d, %Y %I:%M:%S %p")

    @staticmethod
    def hash_password(password: str) -> str:
        pw_hash = bcrypt.generate_password_hash(password=password).decode('utf-8')
        return pw_hash

    @staticmethod
    def check_password(pw_hash: str, password: str) -> bool:
        return bcrypt.check_password_hash(pw_hash=pw_hash, password=password)

    # Verifies the length of the new password and checks that it is not the same as the old one.
    @staticmethod
    def validate_new_password(old_pwd_hash: str, new_pwd: str) -> bool:
        if 7 < len(new_pwd) < 26:
            if len(old_pwd_hash.strip()) == 0:
                return True
            return not bcrypt.check_password_hash(pw_hash=old_pwd_hash, password=new_pwd)
        return False

    # Makes sure the new username is not in use already.
    @staticmethod
    def validate_new_username(old_username: str, new_username: str) -> bool:
        if old_username != new_username and len(new_username) <= 30:
            return User.query.filter_by(username=new_username).first() is None
        return False
