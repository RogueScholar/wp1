from base64 import b64encode
import json
import os
import unittest
from unittest.mock import patch

from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class AppTest(BaseWebTestcase):
    def test_index(self):
        with self.override_db(self.app), self.app.test_client() as client:
            rv = client.get("/")
            self.assertTrue(b"Wikipedia 1.0 Server" in rv.data)

    def test_index_project_count(self):
        projects = []
        for i in range(101):
            projects.append(
                {
                    "p_project": b"Project %s" % str(i).encode("utf-8"),
                    "p_timestamp": b"20181225",
                }
            )

        with self.wp10db.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO projects (p_project, p_timestamp) "
                "VALUES (%(p_project)s, %(p_timestamp)s)",
                projects,
            )
        self.wp10db.commit()

        with self.override_db(self.app), self.app.test_client() as client:
            rv = client.get("/")
            self.assertTrue(
                b"There are currently 101 projects being tracked "
                b"and updated each day." in rv.data
            )

    def test_project_count(self):
        projects = []
        for i in range(101):
            projects.append(
                {
                    "p_project": b"Project %s" % str(i).encode("utf-8"),
                    "p_timestamp": b"20181225",
                }
            )

        with self.wp10db.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO projects (p_project, p_timestamp) "
                "VALUES (%(p_project)s, %(p_timestamp)s)",
                projects,
            )
        self.wp10db.commit()

        with self.override_db(self.app), self.app.test_client() as client:
            rv = client.get("/projects/count")
            data = json.loads(rv.data)
            self.assertEquals(101, data["count"])


class RqTest(unittest.TestCase):
    @patch("wp1.web.app.get_redis_creds")
    def test_rq_no_login(self, patched_get_creds):
        patched_get_creds.return_value = {"host": "localhost", "port": 6379}
        os.environ["RQ_USER"] = "testuser"
        os.environ["RQ_PASS"] = "testpass"  # nosec
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/rq", follow_redirects=True)
            self.assertTrue(b"Please login" in rv.data)

    @patch("wp1.web.app.get_redis_creds")
    def test_rq_login(self, patched_get_creds):
        patched_get_creds.return_value = {"host": "localhost", "port": 6379}
        os.environ["RQ_USER"] = "testuser"
        os.environ["RQ_PASS"] = "testpass"  # nosec
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get(
                "/rq",
                headers={
                    "Authorization": "Basic {}".format(
                        b64encode(b"testuser:testpass").decode("utf-8")
                    )
                },
                follow_redirects=True,
            )
            self.assertFalse(b"Please login" in rv.data)
