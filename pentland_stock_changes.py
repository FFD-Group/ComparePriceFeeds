
from cliq_client import CliqClient
from datetime import date, timedelta
from dotenv import dotenv_values
from xml_feed import XMLFeed
from feed_comparator import FeedComparator
from feed_report import FeedReport
from file_rotator import FileRotator
from url_fetch import UrlFetch
from zoauth_client import ZOAuth2Client


class PentlandStockChanges:

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.today = date.today()
        self.local_filename = "pentland_stock.xml"
        self.past_filename = "pentland_stock_yesterday.xml"
        self.config = dotenv_values(".env")
        self.wd_tokens = {
            "client_id": self.config["WD_CLIENT_ID"],
            "client_secret": self.config["WD_CLIENT_SECRET"],
            "refresh_token": self.config["WD_REFRESH_TOKEN"]
        }
        self.zwd = ZOAuth2Client(self.wd_tokens, "workdrive.zoho")
        self.fetch = UrlFetch("https://www.pentlandwholesale.co.uk/feeds/StockLevels.xml", self.local_filename)
        self.feed_today = XMLFeed(self.local_filename, "productCode")
        self.feed_yesterday = XMLFeed(self.past_filename, "productCode")
        self.fc = FeedComparator(self.feed_today, self.feed_yesterday)
        self.fr = FeedReport(f"Pentland_Stock_{self.today.strftime('%Y-%m-%d')}.xlsx")
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
        self.build_report()
        # self.cliq_post()

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
        self.fetch.fetch_file()

        remote_filename = f"{self.identifier}_stock_{self.today.strftime('%d-%m-%Y')}.xml"
        self.store_file(self.local_filename, remote_filename)

        self.feed_today.loadToDataFrame()
        self.feed_yesterday.loadToDataFrame()

    def compare(self):
        self.new_oos = self.fc.get_newly_oos("stockLevel")
        self.new_in = self.fc.get_back_in_stock("stockLevel")

    def build_report(self):
        self.fr.write_newly_oos(self.new_oos)
        self.fr.write_back_in(self.new_in)

        self.report_link = self.store_file(self.fr.filename)

    def cliq_post(self):
        chat_name = "itgroup"
        card_text = f"Pentland Stock Report for {self.today.strftime('%d-%m-%Y')}"
        card_title = "Pentland Stock Report"
        thumbnail = "https://www.pentlandwholesale.co.uk/skin/frontend/piranha/default/images/logo.png"
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
        print(result)

if __name__ == "__main__":
    psc = PentlandStockChanges("Pentland")
    psc.run()
    print(psc.new_in)
    print(psc.new_oos)