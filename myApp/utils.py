# Utility methods for the routes file
from datetime import datetime
from typing import Union

from myApp import db, User, SavedMessage, log as log


def save_message(user: User, message: str) -> tuple:
    log.info(f"Attempting to save message: {user}\n{message}")
    if user.is_authenticated:
        saved_message = SavedMessage.query.filter_by(saved_userid=user.id, encoded_text=message).first()
        if not saved_message:
            new_save = SavedMessage(encoded_text=message, saved_userid=user.id)
            db.session.add(new_save)
            db.session.commit()
            log.info("Message saved successfully.")
            return "Message Saved.", "success"
        else:
            log.info("Message has already been saved by user.")
            return "Message already saved.", "info"
    log.debug("Something else. User may not have been authenticated, which should not be the case")
    return "Something else.", "warning"


def get_user_saved_messages(user: User) -> list:
    user_saved_messages = SavedMessage.query.filter_by(saved_userid=user.id).all()
    master_list = []
    for msg in user_saved_messages:
        master_list.append(msg.get_as_dict())
    log.info(f"Saved messages: {master_list}")
    return master_list
