# Utility methods for the routes file
from myApp import User, SavedMessage


def save_message(user: User, message: str):
    print(user.username, message)
    if user.is_authenticated:
        print(1)

