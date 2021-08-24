from datetime import date
import os
import unittest

class FileRotator:
    ## TODO: add logging!
    def rotate(self, current: str, last: str, third: str):
        try:
            c_split = self._split_ext(current)
            l_split = self._split_ext(last)
            self._remove(third)
            self._rename(last, (l_split[0] + "_third" + l_split[1]))
            self._rename(current, (c_split[0] + "_last" + c_split[1]))
        except Exception as e:
            raise e

    def _remove(self, filename: str):
        try:
            os.remove(filename)
        except Exception as e:
            raise e
        
    def _rename(self, filename: str, new_name: str):
        try:
            os.rename(filename, new_name)
        except Exception as e:
            raise e

    def _split_ext(self, filename: str):
        try:
            return os.path.splitext(filename)
        except Exception as e:
            raise e

if __name__ == "__main__":
    ## TODO: move test to own file
    ## TODO: more comprehensive test coverage
    from pathlib import Path
    import unittest

    class TestFileRotator(unittest.TestCase):
        def setUp(self):
            # set up test files
            self.of1 = "rot-test_last.xml"
            self.of2 = "rot-test2_third.xml"
            self.tf1 = 'rot-test.xml'
            self.tf2 = 'rot-test2.xml'
            self.tf3 = 'rot-test3.xml'
            Path(self.tf1).touch()
            Path(self.tf2).touch()
            Path(self.tf3).touch()
            self.fr = FileRotator()

        def test_rotate(self):
            self.fr.rotate("rot-test.xml", "rot-test2.xml", "rot-test3.xml")
            self.assertTrue(os.path.exists(self.of1))
            self.assertTrue(os.path.exists(self.of2))
            self.assertFalse(os.path.exists("rot-test.xml"))

        def tearDown(self):
            # remove test files
            if os.path.exists(self.tf1): os.remove(self.tf1)
            if os.path.exists(self.tf2): os.remove(self.tf2)
            if os.path.exists(self.tf3): os.remove(self.tf3)
            if os.path.exists(self.of1): os.remove(self.of1)
            if os.path.exists(self.of2): os.remove(self.of2)

    unittest.main()