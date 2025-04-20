import json
import random

from flask import Blueprint, redirect, render_template, request, session
from sqlalchemy import and_, select

from .extensions import db
from .helper import cors_enabled
from .models import Dare, User

bp = Blueprint("home", __name__)


# @bp.route("/add_user", methods=["OPTIONS", "POST"])
# @cors_enabled(methods=["POST"])
# def add_user():
#     username: str = request.data.decode("utf-8")

#     new_user = User(name=username)
#     db.session.add(new_user)
#     db.session.commit()

#     return "", 201

SET_PASSWORD = "pass"


@bp.route("/check_password", methods=["OPTIONS", "POST"])
@cors_enabled(methods=["POST"])
def check_password():
    password: str = request.data.decode("utf-8")
    correct = password == SET_PASSWORD

    if correct:
        session["role"] = "host"

    return json.dumps(correct), 200


@bp.route("/set_name", methods=["OPTIONS", "POST"])
@cors_enabled(methods=["POST"])
def set_name():
    name: str = request.data.decode("utf-8")
    session["username"] = name
    session["role"] = "player"

    return "", 200


#### PLAYERS


# UNUSED
@bp.route("/add_user", methods=["POST"])
@cors_enabled(methods=["POST"])
def add_user():
    name: str = request.data.decode("utf-8")

    if not name:
        return "Missing username", 400

    # current_users = session.get("users", [])
    # if name in current_users:
    #     return "Username already exists", 400

    # session["users"] = current_users + [name]

    new_user = User(name=name)

    if (
        db.session.scalars(
            select(User.name).where(and_(User.name == name, User.removed == False))  # noqa: E712
        ).first()
        is not None
    ):
        return "Username already exists", 400

    db.session.add(new_user)
    db.session.commit()

    return "", 200


@bp.route("/remove_user", methods=["POST"])
@cors_enabled(methods=["POST"])
def remove_user():
    name: str = request.data.decode("utf-8")

    user = db.session.scalars(select(User).where(User.name == name)).first()
    if user:
        user.removed = True
        db.session.commit()

    # current_users: list = session.get("users", [])
    # try:
    #     user_id = current_users.index(name)
    #     current_users.pop(user_id)
    #     session["users"] = current_users
    # except ValueError:
    #     return "", 200

    return "", 200


@bp.route("/remove_all_users", methods=["POST"])
@cors_enabled(methods=["POST"])
def remove_all_users():
    users = db.session.scalars(select(User).where(User.removed == False)).all()  # noqa: E712
    for user in users:
        user.removed = True

    db.session.commit()

    return "", 200


def get_active_users():
    """Get users who have `removed == False`, must be run in app context"""
    rows = db.session.scalars(select(User).where(User.removed == False)).all()  # noqa: E712
    return rows


@bp.route("/get_users", methods=["GET"])
@cors_enabled(methods=["GET"])
def get_users():
    return [user.name for user in get_active_users()], 200


@bp.route("/pick_user", methods=["GET"])
@cors_enabled(methods=["GET"])
def pick_user():
    # rows = db.session.scalars(
    #     select(Dare.by).where(Dare.used == False).distinct()  # noqa: E712
    # ).all()
    # print(rows)

    # rows = session.get("users", [])

    rows = get_active_users()
    # Reset all picked values when everyone has been picked
    if all([user.picked for user in rows]):
        for user in rows:
            user.picked = False

    user = random.choice([row for row in rows if not row.picked])
    user.picked = True

    db.session.commit()

    return user.name, 200


#### DARES


@bp.route("/add_dare", methods=["OPTIONS", "POST"])
@cors_enabled(methods=["POST"])
def add_dare():
    data: dict = json.loads(request.data.decode("utf-8"))

    new_dare = Dare(content=data["content"], by=session.get("username", ""))
    db.session.add(new_dare)
    db.session.commit()

    return "", 201


@bp.route("/get_dares", methods=["GET"])
@cors_enabled(methods=["GET"])
def get_dares():
    rows = db.session.scalars(select(Dare).where(Dare.used == False)).all()  # noqa: E712
    print(rows)

    return [
        {"content": row.content, "by": row.by, "played": row.played} for row in rows
    ], 200


@bp.route("/set_used", methods=["POST"])
@cors_enabled(methods=["POST"])
def set_used():
    rows = db.session.scalars(select(Dare)).all()
    for dare in rows:
        dare.used = True

    db.session.commit()

    return "", 200


@bp.route("/set_used_individual", methods=["POST"])
@cors_enabled(methods=["POST"])
def set_used_individual():
    data: dict = json.loads(request.data.decode("utf-8"))

    dares_toupdate = db.session.scalars(
        select(Dare).where(Dare.content == data["content"] and Dare.by == data["by"])
    ).all()

    for dare in dares_toupdate:
        dare.used = True

    db.session.commit()

    return "", 200


@bp.route("/set_played", methods=["POST"])
@cors_enabled(methods=["POST"])
def set_played():
    data: dict = json.loads(request.data.decode("utf-8"))

    dares_toupdate = db.session.scalars(
        select(Dare).where(Dare.content == data["content"] and Dare.by == data["by"])
    ).all()
    for dare in dares_toupdate:
        dare.played = True

    # db.session.commit()

    # Reset `played` status if every dare has been played
    test = db.session.scalars(
        select(Dare.id).where(and_(Dare.used == False, Dare.played == False))  # noqa: E712
    ).first()
    print("🎈🎈🎈", test)
    if test is None:
        print("Updating all dares to be not played")
        dares = db.session.scalars(select(Dare).where(Dare.used == False)).all()  # noqa: E712
        print(dares)
        for dare in dares:
            dare.played = False

    db.session.commit()

    return "", 200


#### PAGES


@bp.route("/")
@bp.route("/home")
def home():
    return render_template("main/home.html")


@bp.route("/host")
def host():
    if session.get("role") != "host":
        return redirect("/")
    return render_template("main/host.html")


@bp.route("/player")
def player():
    return render_template("main/player.html")
