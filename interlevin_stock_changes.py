
from cliq_client import CliqClient
from datetime import date, timedelta
from dotenv import dotenv_values
from feed_comparator import FeedComparator
from feed_report import FeedReport
from file_rotator import FileRotator
from url_fetch import UrlFetch
from xml_feed import XMLFeed
from zoauth_client import ZOAuth2Client

class InterlevinStockChanges:

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.today = date.today()
        self.local_filename = "interlevin_stock.xml"
        self.past_filename = "interlevin_stock_yesterday.xml"
        self.fileRot = FileRotator(self.local_filename, self.past_filename)
        self.config = dotenv_values(".env")
        self.wd_tokens = {
            "client_id": self.config["WD_CLIENT_ID"],
            "client_secret": self.config["WD_CLIENT_SECRET"],
            "refresh_token": self.config["WD_REFRESH_TOKEN"]
        }
        self.zwd = ZOAuth2Client(self.wd_tokens, "workdrive.zoho")
        self.fetch = UrlFetch("https://www.interlevin.co.uk/all-products.xml", self.local_filename)
        self.feed_today = XMLFeed(self.local_filename, "Product_Code", "Product")
        self.feed_yesterday = XMLFeed(self.past_filename, "Product_Code", "Product")
        self.fc = FeedComparator(self.feed_today, self.feed_yesterday)
        self.fr = FeedReport(f"Interlevin_Stock_{self.today.strftime('%Y-%m-%d')}.xlsx")
        self.cliq_tokens = {
            "client_id": self.config["CLIQ_CLIENT_ID"],
            "client_secret": self.config["CLIQ_CLIENT_SECRET"],
            "refresh_token": self.config["CLIQ_REFRESH_TOKEN"],
            "access_token": self.config["CLIQ_ACCESS_TOKEN"]
        }
        self.cliq = CliqClient(self.cliq_tokens)

    def run(self):
        self.prepare()
        self.compare()
        if len(self.new_oos) > 0 or len(self.new_in) > 0:
            self.build_report()
        self.cliq_post()

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
        self.today_file_link = response["data"][0]["attributes"]["Permalink"]
        print(f"File {filename} stored at:", self.today_file_link, f"as {remote_filename}")
        return self.today_file_link

    def prepare(self):
        self.fileRot.rotateFiles()
        self.fetch.fetch_file()

        remote_filename = f"{self.identifier}_stock_{self.today.strftime('%d-%m-%Y')}.xml"
        self.store_file(self.local_filename, remote_filename)

        self.feed_today.loadToDataFrame()
        self.feed_yesterday.loadToDataFrame()

    def compare(self):
        self.new_oos = self.fc.get_newly_oos_no_levels("Stock")
        self.new_in = self.fc.get_back_in_stock_no_levels("Stock")

    def build_report(self):
        self.fr.write_newly_oos(self.new_oos, True)
        self.fr.write_back_in(self.new_in)

        self.report_link = self.store_file(self.fr.filename)

    def cliq_post(self):
        if len(self.new_in) > 0 or len(self.new_oos) > 0:
            chat_name = "itgroup"
            card_text = f"Interlevin Stock Report for {self.today.strftime('%d-%m-%Y')}"
            card_title = "Interlevin Stock Report"
            thumbnail = "https://www.interlevin.co.uk/library/logo_5.png"
            table_title = "Detected Changes"
            table_hdrs = ["Change", "Count"]
            table_rws = [
                {
                    "Change": "New OOS",
                    "Count": len(self.new_oos), 
                }, {
                    "Change": "New in",
                    "Count": len(self.new_in), 
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
        else:
            result = self.cliq.postSimpleMessage("itgroup", f"Interlevin Stock Report For {self.today.strftime('%d-%m-%Y')}: No changes detected.")

        print(result)