from datetime import date
from typing import Union
from dotenv import dotenv_values
from ftplib import FTP

class FtpFetch:

    def __init__(self) -> None:
        config = dotenv_values(".env")
        self.username = config["UROPA_USER"]
        self.password = config["UROPA_PASS"]
        self.ftp_url = config["UROPA_FTP"]
        self.ftp = FTP(self.ftp_url)
        self.ftp.login(self.username, self.password)

    def fetch_stock_file(self):
        with open("today.csv", 'wb') as local_file:
            self.ftp.retrbinary("RETR Stock.csv", local_file.write)

    def fetch_specific_file(self, file_starts_with: str) -> str:
        file_list = self.ftp.nlst()
        matching = [file for file in file_list if file_starts_with in file]

        if len(matching) == 1:
            with open(matching[0], 'wb') as local_file:
                self.ftp.retrbinary(f"RETR {matching[0]}", local_file.write)
            return matching[0]
        else:
            return False

    def find_filename(self, starts_with: str) -> str:
        file_list = self.ftp.nlst()
        matching = [file for file in file_list if starts_with in file]

        if len(matching) == 1:
            return matching[0]
        else:
            return False
    
