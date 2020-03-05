import attr
import flask

import wp1.logic.project as logic_project
from wp1.web.db import get_db

projects = flask.Blueprint("projects", __name__)


@projects.route("/")
def list_():
    wp10db = get_db("wp10db")
    projects = logic_project.list_all_projects(wp10db)
    return flask.jsonify(list(project.to_web_dict() for project in projects))


@projects.route("/count")
def count():
    wp10db = get_db("wp10db")
    count = logic_project.count_projects(wp10db)
    return flask.jsonify({"count": count})
