from cliq_client import CliqClient
from datetime import date, timedelta
from dotenv import dotenv_values
from feed_comparator import FeedComparator
from feed import Feed
from feed_report import FeedReport
from ftp_fetch import FtpFetch
from zoauth_client import ZOAuth2Client


class RBPriceChanges:

    def __init__(self) -> None:
        self.ftp = FtpFetch()
        self.config = dotenv_values(".env")
        self.wd_tokens = {
                "client_id": self.config["WD_CLIENT_ID"],
                "client_secret": self.config["WD_CLIENT_SECRET"],
                "refresh_token": self.config["WD_REFRESH_TOKEN"]
            }
        self.wd = ZOAuth2Client(self.wd_tokens, "workdrive.zoho")
        self.cliq_tokens = {
            "client_id": self.config["CLIQ_CLIENT_ID"],
            "client_secret": self.config["CLIQ_CLIENT_SECRET"],
            "refresh_token": self.config["CLIQ_REFRESH_TOKEN"],
            "access_token": self.config["CLIQ_ACCESS_TOKEN"]
        }
        cliq = CliqClient(self.cliq_tokens)

    def run(self):
        self.fetch_today_feed()
        self.store_today_feed()
        self.load_feeds()
        self.compare()
        self.cliq_report()

    def fetch_today_feed(self):
        # Get the file starting with "Price_" + <today's date> in it's name
        self.today = date.today().strftime("%Y%m%d")
        today_filename = f"Price_{self.today}"
        
        self.today_feed_filename = self.ftp.fetch_specific_file(today_filename)

    def store_today_feed(self):
        params = {
            "filename": self.today_feed_filename,
            "parent_id": self.config["WD_FOLDER_ID"],
            "override-name-exist": False
        }
        data = {
            "content": open(self.today_feed_filename, 'rb')
        }
        response = self.wd.query("/api/v1/upload", p=params, file=data)
        self.link = response["data"][0]["attributes"]["Permalink"]
        print(f"File {self.today_feed_filename} stored at:", self.link, f"as {self.today_feed_filename}")
        return self.link

    def load_feeds(self):
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
        yesterday_filename_starts_with = f"Price_{yesterday}"
        yesterday_filename = self.ftp.find_filename(yesterday_filename_starts_with)

        self.today_feed = Feed(self.today_feed_filename)
        self.yesterday_feed = Feed(yesterday_filename)

        self.today_feed.loadToDataFrame()
        self.yesterday_feed.loadToDataFrame()

    def compare(self):
        ## compare the prices in the feed to see what has changed
        self.fc = FeedComparator(self.today_feed, self.yesterday_feed)

        self.increased = list()
        self.decreased = list()
        self.unchanged = 0

        print("Finding diffs...")
        for product in self.today_feed.get_next_product("ProductCode"):
            values = self.fc.get_comparable_feed_values(product, "WebOnlyPrice")
            if len(values) >= 2:
                today_web_price = float(values[0][0])
                yesterday_web_price = float(values[1][0])
                difference = today_web_price - yesterday_web_price
                if difference < 0:
                    self.decreased.append(product, difference)
                elif difference > 0:
                    self.increased.append(product, difference)
                else:
                    self.unchanged += 1

        if len(self.increased) > 0:
            diff_list = list()
            for sku, diff in self.increased:
                diff_list.append(diff)
            self.increase_avg = sum(diff_list)/len(diff_list)
        else:
            self.increase_avg = 0.00

        if len(self.decreased) > 0:
            diff_list = list()
            for sku, diff in self.decreased:
                diff_list.append(diff)
            self.decrease_avg = sum(diff_list)/len(diff_list)
        else:
            self.decrease_avg = 0.00

    def cliq_report(self):
        if len(self.increased) > 0 or len(self.decreased) > 0:
            print("Increased:", len(self.increased))
            fr = FeedReport("Price_report-test.xlsx")
            fr.write_prices(self.increased, "increased", self.today_feed)
            print("Decreased:", len(self.decreased))
            fr.write_prices(self.decreased, "decreased", self.today_feed)
            print("No change:", self.unchanged)

            report_rows = [
                ["Increased:", len(self.increased), "(Avg: £" + str(self.increase_avg) + ")"],
                ["Decreased:", len(self.decreased), "(Avg: £" + str(self.decrease_avg) + ")"],
                ["unchanged:", self.unchanged],
            ]

            fr.write_report_sheet(report_rows, f"Report-{self.today}")

            params = {
                "filename": f"Uropa_price_report-{self.today}",
                "parent_id": self.config["WD_FOLDER_ID"],
                "override-name-exist": False
            }
            data = {
                "content": open(fr.filename, 'rb')
            }
            response = self.wd.query("/api/v1/upload", p=params, file=data)
            link = response["data"][0]["attributes"]["Permalink"]

            # post card with table to cliq
            chat_name = "itgroup"
            card_text = f"RB Price Report for {self.today}"
            card_title = "RB Price Report"
            thumbnail = "https://media.nisbets.com/images/theme/uropa/logo/uropa-logo.svg"
            table_title = "Detected Changes"
            table_hdrs = ["Change", "Count", "Avg Diff"]
            table_rws = [
                {
                    "Change": "Increase",
                    "Count": len(self.increased),
                    "Avg Diff": self.increase_avg
                }, {
                    "Change": "Decrease",
                    "Count": len(self.decreased), 
                    "Avg Diff": self.decrease_avg
                }, {
                    "Change": "No Change",
                    "Count": self.unchanged,
                    "Avg Diff": "-"
                }
            ]
            btns = [{
                "label": "View Report",
                "type": "+",
                "action": {
                    "type": "open.url",
                    "data": {
                        "web": self.link
                    }
                }
            }]

            response = self.cliq.postInlineCard(chat_name, card_text, card_title, thumbnail, table_title, table_hdrs, table_rws, btns)
            print(response)
        else:
            response = self.cliq.postSimpleMessage("itgroup", f"RB Price Report For {self.today}: No changes detected.")
            print(response)
