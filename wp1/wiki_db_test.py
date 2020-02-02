import unittest.mock

from wp1 import wiki_db
from wp1.base_db_test import get_test_connect_creds
from wp1.environment import Environment


class WikiDbTest(unittest.TestCase):

  @unittest.mock.patch("wp1.db.ENV", Environment.DEVELOPMENT)
  @unittest.mock.patch("wp1.db.CREDENTIALS", get_test_connect_creds())
  def test_connect_works_with_creds(self):
    self.assertIsNotNone(wiki_db.connect())
