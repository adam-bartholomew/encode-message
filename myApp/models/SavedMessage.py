from myApp import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func


class SavedMessage(db.Model, UserMixin):
    """Define the structure of the messages that can be saved by a user of the flask app.
    """
    __tablename__ = 'saved_messages'

    id = Column(Integer, primary_key=True)
    encoded_text = Column(Text, nullable=False)
    saved_userid = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    saved_datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __init__(self, *args, **kwargs) -> None:
        self.encoded_text = kwargs.get("encoded_text")
        self.saved_userid = kwargs.get("saved_userid")
        self.saved_datetime = kwargs.get("saved_datetime")

    def __repr__(self) -> str:
        return f"<Saved Message {self.id}>:(" \
               f"encoded_text=\"{self.encoded_text}\"" \
               f", saved_userid=\"{self.saved_userid}\"" \
               f", saved_datetime=\"{self.saved_datetime}\")"

    def get_as_dict(self) -> dict:
        message_dict = dict(id=self.id, encoded_text=self.encoded_text, saved_userid=self.saved_userid,
                            saved_datetime=self.saved_datetime)
        return message_dict
