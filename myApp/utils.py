# Utility methods for the application.
from myApp import db, User, SavedMessage, log
from config import ROWS_PER_PAGE


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


'''
def get_user_saved_messages(user: User) -> list:
    user_saved_messages = SavedMessage.query.filter_by(saved_userid=user.id).all()
    master_list = []
    for msg in user_saved_messages:
        master_list.append(msg.get_as_dict())
    return master_list
'''


def delete_saved_message(saved_message_id: int) -> tuple:
    saved_message = SavedMessage.query.filter_by(id=saved_message_id).first()
    if saved_message:
        db.session.delete(saved_message)
        db.session.commit()
        log.info(f"Deleted: {saved_message}")
        return "Saved message deleted", "success"
    return "Message was not be deleted", "warning"

