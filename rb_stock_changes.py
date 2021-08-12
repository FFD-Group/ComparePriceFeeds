
from cliq_client import CliqClient
from datetime import date, timedelta
from dotenv import dotenv_values
from feed import Feed
from feed_comparator import FeedComparator
from feed_report import FeedReport
from file_rotator import FileRotator
from ftp_fetch import FtpFetch
from zoauth_client import ZOAuth2Client


class RBStockChanges:

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.config = dotenv_values(".env")
        self.wd_tokens = {
            "client_id": self.config["WD_CLIENT_ID"],
            "client_secret": self.config["WD_CLIENT_SECRET"],
            "refresh_token": self.config["WD_REFRESH_TOKEN"]
        }
        self.zwd = ZOAuth2Client(self.wd_tokens, "workdrive.zoho")
        self.fileRot = FileRotator()
        self.ftp = FtpFetch()
        self.feed_today = Feed("today.csv")
        self.feed_yesterday = Feed("yesterday.csv")
        self.fc = FeedComparator(self.feed_today, self.feed_yesterday)
        self.fr = FeedReport()
        self.cliq_tokens = {
            "client_id": self.config["CLIQ_CLIENT_ID"],
            "client_secret": self.config["CLIQ_CLIENT_SECRET"],
            "refresh_token": self.config["CLIQ_REFRESH_TOKEN"],
            "access_token": self.config["CLIQ_ACCESS_TOKEN"]
        }
        self.cliq = CliqClient(self.cliq_tokens)

    def store_file(self, filename: str, store_as: str=None) -> str:
        remote_filename = store_as if store_as else filename
        params = {
            "filename": remote_filename,
            "parent_id": self.config["WD_FOLDER_ID"],
            "override-name-exist": False
        }
        data = {
            "content": open(filename, 'rb')
        }
        response = self.zwd.query("/api/v1/upload", p=params, file=data)
        link = response["data"][0]["attributes"]["Permalink"]
        print(f"File {filename} stored at:", link, f"as {remote_filename}")
        return link

    def prepare(self):
        self.fileRot.rotateFiles()
        self.ftp.fetch_file()

        today = date.today()
        remote_filename = f"{self.identifier}_stock_{today.strftime('%d-%m-%Y')}.csv"
        self.store_file("today.csv", remote_filename)

        self.feed_today.loadToDataFrame()
        self.feed_yesterday.loadToDataFrame()

    def compare(self):
        self.new_oos = self.fc.get_newly_oos()
        self.new_in = self.fc.get_back_in_stock()
        self.dropped = self.fc.get_newly_dropped_lines()

    def report(self):
        self.fr.write_newly_oos(self.new_oos)
        self.fr.write_back_in(self.new_in)
        self.fr.write_dropped(self.dropped)

        self.report_link = self.store_file(self.fr.filename)

    def cliq_post(self):
        today = date.today().strftime("%d-%m-%Y")
        chat_name = "itgroup"
        card_text = f"RB Stock Report for {today}"
        card_title = "RB Stock Report"
        thumbnail = "https://media.nisbets.com/images/theme/uropa/logo/uropa-logo.svg"
        table_title = "Detected Changes"
        table_hdrs = ["Change", "Count"]
        table_rws = [
            {
                "Change": "New OOS",
                "Count": len(self.new_oos), 
            }, {
                "Change": "New in",
                "Count": len(self.new_in), 
            }, {
                "Change": "Dropped",
                "Count": len(self.dropped)
            }
        ]
        btns = [{
            "label": "View Report",
            "type": "+",
            "action": {
                "type": "open.url",
                "data": {
                    "web": self.report_link
                }
            }
        }]

        result = self.cliq.postInlineCard(chat_name, card_text, card_title, thumbnail, table_title, table_hdrs, table_rws, btns)
        print(result)