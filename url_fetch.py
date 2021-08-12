from datetime import date
from dotenv import dotenv_values
from typing import Union
import requests
from zoauth_client import ZOAuth2Client

class UrlFetch:

    def __init__(self, url: str, local_filename) -> None:
        self.config = dotenv_values(".env")
        self.url = url
        self.local_filename = local_filename

    def fetch_file(self, uploadToWorkDrive=False, remote_filename=None):
        '''
        Download and optionally upload file.
        @param uploadToWorkDrive        Default False. Whether to upload the file to Workdrive.
        @return str                     The downloaded filename or it's permalink from upload.
        '''
        with requests.get(self.url, stream=True) as req:
            req.raise_for_status()
            with open(self.local_filename, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        if uploadToWorkDrive:
            remote_name = remote_filename if remote_filename else self.local_filename
            link = self.upload_to_zwd(self.local_filename, remote_name)
        else: link = None
        return link if link else f"Downloaded as: {self.local_filename}"

    def upload_to_zwd(self, local_filename: str, remote_filename: str) -> str:
        '''
        Upload the given local file to WorkDrive.
        @param local_filename       The local file to upload
        @param remote_filename      The filename to upload as
        @return str                 The permalink of the uploaded file
        '''
        wd_tokens = {
                    "client_id": self.config["WD_CLIENT_ID"],
                    "client_secret": self.config["WD_CLIENT_SECRET"],
                    "refresh_token": self.config["WD_REFRESH_TOKEN"]
                }
        wd = ZOAuth2Client(wd_tokens, "workdrive.zoho")

        params = {
            "filename": remote_filename,
            "parent_id": self.config["WD_FOLDER_ID"],
            "override-name-exist": False
        }
        data = {
            "content": open(local_filename, 'rb')
        }
        response = wd.query("/api/v1/upload", p=params, file=data)
        return response["data"][0]["attributes"]["Permalink"]
    

if __name__ == "__main__":
    uf = UrlFetch("https://www.pentlandwholesale.co.uk/feeds/StockLevels.xml", "Pentland-Stock-Test.xml")
    f = uf.fetch_file(True)
    print(f)