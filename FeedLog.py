from datetime import datetime
from pathlib import Path

class FeedLog:
    
    def __init__(self, filename: str="feedlog"):
        self.log = filename + ".log"
        Path(self.log).touch()

    def log_line(self, msg: str):
        t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(self.log, 'a') as log:
            log.write(f"[{t}]: {msg}")

if __name__ == "__main__":
    from dateutil.parser import parse
    import os
    from typing import Tuple
    import unittest

    class TestFeedLog(unittest.TestCase):

        def setUp(self):
            self.log_file = "test-log"
            self.feed_log = FeedLog(self.log_file)

        def test_create_log_without_name(self):
            f = FeedLog()
            self.assertTrue(os.path.exists("feedlog.log"))

        def test_create_log_with_name(self):
            self.assertTrue(os.path.exists(self.log_file + ".log"))

        def test_log_line_exists(self):
            log_str = "Testing my feed log."

            self.feed_log.log_line(log_str)
            found = False
            with open(self.log_file + ".log", 'r') as log:
                for line in log:
                    if log_str in line: found = True
            self.assertTrue(found)

        def test_log_line_has_datetime(self):
            log_str = "Testing my feed log."
            self.feed_log.log_line(log_str)
            with open(self.log_file + ".log", 'r') as log:
                for line in log:
                    if log_str in line:
                        self.assertIsInstance(
                            parse(line, fuzzy=True), (datetime, Tuple), "Parse didn't return a datetime or Tuple obj."
                        )

        def test_log_has_log_extension(self):
            expected_ext = ".log"
            name, ext = os.path.splitext(self.log_file + ".log")
            self.assertEqual(ext, expected_ext)

        def tearDown(self):
            if os.path.exists("feedlog.log"): os.remove("feedlog.log")
            if os.path.exists(self.log_file + ".log"): os.remove(self.log_file + ".log")

    unittest.main()


