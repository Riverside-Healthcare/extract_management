"""EM Web Startup."""
# Extract Management 2.0
# Copyright (C) 2020  Riverside Healthcare, Kankakee, IL

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys
from pathlib import Path

from em_web.extensions import (
    cache,
    compress,
    db,
    executor,
    htmlmin,
    login_manager,
    migrate,
    redis_client,
    sess,
    toolbar,
    web_assets,
)

from flask import Flask, render_template  # isort:skip

sys.path.append(str(Path(__file__).parents[1]) + "/scripts")
from error_print import full_stack  # isort:skip


def create_app():
    """Create app.

    :returns: app.
    """
    # pylint: disable=W0621
    app = Flask(__name__)

    if app.config["ENV"] == "development":
        app.config.from_object("em_web.config.DevConfig")

    elif app.config["ENV"] == "test":
        app.config.from_object("em_web.config.TestConfig")

    else:
        app.config.from_object("em_web.config.Config")

    compress.init_app(app)
    web_assets.init_app(app)

    # auth
    login_manager.init_app(app)
    login_manager.login_view = app.config["LOGIN_VIEW"]
    login_manager.login_message = app.config["LOGIN_MESSAGE"]

    sess.init_app(app)

    # database
    db.init_app(app)
    migrate.init_app(app, db, directory=app.config["MIGRATIONS"])

    # web cache
    cache.init_app(app)
    cache.clear()
    # run tasks off main thread
    executor.init_app(app)

    # redis
    redis_client.init_app(app)

    # html min
    htmlmin.init_app(app)

    with app.app_context():

        # pylint: disable=W0611
        from em_web import cli
        from em_web.web import assets  # noqa: F401
        from em_web.web import (
            admin,
            auth,
            connection,
            dashboard,
            executors,
            filters,
            project,
            saml_auth,
            table,
            task,
        )

        app.register_blueprint(saml_auth.login_bp)
        app.register_blueprint(admin.admin_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(connection.connection_bp)
        app.register_blueprint(project.project_bp)
        app.register_blueprint(task.task_bp)
        app.register_blueprint(dashboard.dashboard_bp)
        app.register_blueprint(table.table_bp)
        app.register_blueprint(executors.executors_bp)
        app.register_blueprint(filters.filters_bp)
        app.register_blueprint(cli.cli_bp)

        if app.config["DEBUG"]:
            toolbar.init_app(app)
            assets.cache = False
            assets.manifest = False

        return app


app = create_app()


@app.errorhandler(404)
@app.errorhandler(500)
def error_message(error):
    """Return error page for 404 and 500 errors including the specific error message.

    :param error: error message
    :return: json web response with error message:

    .. code-block:: python

        {"error": "messsage"}

    """
    return render_template(
        "error.html.j2",
        message="<strong>" + str(error).replace(":", "</strong>:"),
        trace=full_stack(),
        title="That was an error",
    )


if __name__ == "__main__":
    app.run()
