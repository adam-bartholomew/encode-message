from myApp import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, DateTime


class UserModel(db.Model, UserMixin):
    """Define the structure of the "User" object used in the flask app.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(80), unique=True)
    creation_datetime = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    last_modified_datetime = Column(DateTime(timezone=False), server_default=func.now())
    creation_userid = Column(String(25), nullable=False, server_default='flask_app')
    last_modified_userid = Column(String(25), server_default='flask_app')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.id}>:" \
               f"   username={self.username}" \
               f"   first_name={self.first_name}" \
               f"   last_name={self.last_name}" \
               f"   email={self.email}"

    def set_empty_properties(self):
        if self.first_name is None:
            self.first_name = ""
        if self.last_name is None:
            self.last_name = ""
        if self.email is None:
            self.email = ""

    @staticmethod
    def get_formatted_date(date):
        if date is None:
            return ""
        return date.strftime("%B %d, %Y %I:%M:%S %p")
