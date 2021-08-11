import os

class FileRotator:

    def __init__(self, current_filename=None, past_filename=None):
        self.current_filename = current_filename if current_filename else "today.csv"
        self.past_filename = past_filename if past_filename else "yesterday.csv"

    def rotateFiles(self):
        if (os.path.exists(self.past_filename)):
            os.remove(self.past_filename)
        if (os.path.exists(self.current_filename)):
            os.rename(self.current_filename, self.past_filename)

if __name__ == "__main__":
    fr = FileRotator()
    fr.rotateFiles()