import urllib.parse

import attr


def validate_list(items):
  item_list = items.split("\n")
  invalid_article_names = []
  valid_article_names = []
  forbiden_chars = []
  for item in item_list:
    is_valid = True
    item = item.strip().replace(" ", "_")
    decoded_item = urllib.parse.unquote(item)
    len_item = len(decoded_item.encode("utf-8"))
    char_set = ["#", "<", ">", "[", "]", "{", "}", "|"]
    if len_item > 256:
      forbiden_chars.append('length greater than 256 bytes')
      invalid_article_names.append(decoded_item)
      is_valid = False
      continue
    for forbiden_character in char_set:
      if forbiden_character in decoded_item:
        forbiden_chars.append(forbiden_character)
        if is_valid:
          invalid_article_names.append(decoded_item)
        is_valid = False
    if is_valid:
      article_name = decoded_item.replace(
          "https://en.wikipedia.org/wiki/",
          "").replace("https://en.wikipedia.org/w/index.php?title=", "")
      valid_article_names.append(article_name)
  return (valid_article_names, invalid_article_names, forbiden_chars)


def insert_selection(wp10db, selection):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO selections
      (s_id, s_builder_id, s_content_type, s_updated_at)
      VALUES (%(s_id)s, %(s_builder_id)s, %(s_content_type)s, %(s_updated_at)s)
    ''', attr.asdict(selection))
  wp10db.commit()
