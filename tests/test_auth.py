# flake8: noqa,
# pylint: skip-file
import json
import os

import pytest
from flask import g, url_for
from flask_login import current_user


def test_index(em_web_app):
    """Verify that rediction to login page works.

    Parameters:
        em_web_app: client fixture
    """
    res = em_web_app.get("/")
    # should redirect to login page
    if not em_web_app.application.config.get("TEST"):
        assert res.status_code == 302
        assert "/login" in res.get_data(as_text=True)


def login(em_web_app, username, password):
    assert em_web_app.get("/login").status_code == 200

    return em_web_app.post(
        url_for("auth_bp.login"),
        data=dict(user=username, password=password),
        follow_redirects=True,
    )


def logout(em_web_app):
    return em_web_app.get("/logout", follow_redirects=True)


@pytest.mark.options(env="test")
def test_login_logout(em_web_app):
    """Make sure login and logout works."""

    username = user = "mr-cool"
    password = ""

    rv = login(em_web_app, username, password)
    assert rv.status_code == 200
    assert b"Extract Management 2.0 - Mr Cool's Projects" in rv.data

    assert current_user.get_id()

    # verify we stay logged in
    rv = em_web_app.get("/login", follow_redirects=True)
    assert rv.status_code == 200
    assert b"Extract Management 2.0 - Mr Cool's Projects" in rv.data

    rv = logout(em_web_app)
    assert rv.status_code == 200
    assert b"Bye." in rv.data

    rv = login(em_web_app, username + "x", password)
    print(rv.data)
    assert b"Invalid login, please try again!" in rv.data


def test_not_authorized(em_web_app):
    rv = em_web_app.get("/not_authorized", follow_redirects=True)
    assert rv.status_code == 200


def test_bad_next(em_web_app):
    assert em_web_app.get("/login").status_code == 200

    username = user = "mr-cool"
    password = ""

    return em_web_app.post(
        url_for("auth_bp.login"),
        data=dict(user=username, password=password, next="this_is_junk"),
        follow_redirects=True,
    )


def test_log_login(em_web_app):
    from em_web.web.auth import log_login

    assert log_login("mr-cool", 1) is None
