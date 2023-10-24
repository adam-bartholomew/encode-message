# Utility methods for the application.
from myApp import db, User, SavedMessage, log
from datetime import datetime


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


def delete_saved_message(saved_message_id: int) -> tuple:
    saved_message = SavedMessage.query.filter_by(id=saved_message_id).first()
    if saved_message:
        db.session.delete(saved_message)
        db.session.commit()
        log.info(f"Deleted: {saved_message}")
        return "Saved message deleted", "success"
    return "Message was not be deleted", "warning"


def delete_account(user_id: int) -> tuple:
    user = User.query.filter_by(id=user_id).first()
    saved_messages = SavedMessage.query.filter_by(saved_userid=user.id).all()
    if user:
        if saved_messages:
            for saved_message in saved_messages:
                db.session.delete(saved_message)
            log.info(f"Deleted: {saved_messages}")
        db.session.delete(user)
        db.session.commit()
        log.info(f"Deleted: {user}")
        return "Account deleted", "success"
    return "Account not deleted - something went wrong", "error"


def update_profile(user: User, new_username: str, new_password, new_first_name, new_last_name, new_email) -> tuple:
    has_changes = False
    if user.validate_new_username(user.username, new_username):
        has_changes = True
        user.username = new_username
    if user.validate_new_password(user.password, new_password):
        has_changes = True
        user.password = user.hash_password(new_password)
    if user.first_name != new_first_name:
        has_changes = True
        user.first_name = new_first_name
    if user.last_name != new_last_name:
        has_changes = True
        user.last_name = new_last_name
    if user.email != new_email:
        has_changes = True
        user.email = new_email

    if has_changes:
        user.last_modified_datetime = datetime.now()
        user.last_modified_userid = new_username
        user.clear_empty_properties()
        log.info(f"Saving {user}")
        db.session.commit()
        user = User.query.filter_by(username=user.username).first_or_404()
        user.set_empty_properties()
        return "Profile Updated", "success"
    log.info(f"Info was not changed for {user}")
    return None, None
