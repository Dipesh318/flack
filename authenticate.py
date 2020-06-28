from flask import session


def auth():
    if session.get("username") is None:
        return False
    return True