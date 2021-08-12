from cliq_client import CliqClient
from datetime import date, timedelta
from dotenv import dotenv_values
from feed_comparator import FeedComparator
from feed import Feed
from feed_report import FeedReport
from ftp_fetch import FtpFetch
from zoauth_client import ZOAuth2Client
## fetch the latest price file from the FTP

# Get the file starting with "Price_" + <today's date> in it's name
today = date.today().strftime("%Y%m%d")
today_filename = f"Price_{today}"
ftp = FtpFetch()
local_filename = ftp.fetch_specific_file(today_filename)
config = dotenv_values(".env")
wd_tokens = {
            "client_id": config["WD_CLIENT_ID"],
            "client_secret": config["WD_CLIENT_SECRET"],
            "refresh_token": config["WD_REFRESH_TOKEN"]
        }
wd = ZOAuth2Client(wd_tokens, "workdrive.zoho")

params = {
    "filename": local_filename,
    "parent_id": config["WD_FOLDER_ID"],
    "override-name-exist": False
}
data = {
    "content": open(local_filename, 'rb')
}
response = wd.query("/api/v1/upload", p=params, file=data)
link = response["data"][0]["attributes"]["Permalink"]
print(f"File {local_filename} stored at:", link, f"as {local_filename}")

yesterday = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
yesterday_filename_starts_with = f"Price_{yesterday}"
yesterday_filename = ftp.find_filename(yesterday_filename_starts_with)

assert yesterday_filename
assert local_filename

today_feed = Feed(local_filename)
yesterday_feed = Feed(yesterday_filename)

today_feed.loadToDataFrame()
yesterday_feed.loadToDataFrame()

## compare the prices in the feed to see what has changed
fc = FeedComparator(today_feed, yesterday_feed)

increased = list()
decreased = list()
unchanged = 0

print("Finding diffs...")
for product in today_feed.get_next_product("ProductCode"):
    values = fc.get_comparable_feed_values(product, "WebOnlyPrice")
    if len(values) >= 2:
        today_web_price = float(values[0][0])
        yesterday_web_price = float(values[1][0])
        difference = today_web_price - yesterday_web_price
        if difference < 0:
            decreased.append(product, difference)
        elif difference > 0:
            increased.append(product, difference)
        else:
            unchanged += 1

## report on changes

if len(increased) > 0:
    diff_list = list()
    for sku, diff in increased:
        diff_list.append(diff)
    increase_avg = sum(diff_list)/len(diff_list)
else:
    increase_avg = 0.00

if len(decreased) > 0:
    diff_list = list()
    for sku, diff in decreased:
        diff_list.append(diff)
    decrease_avg = sum(diff_list)/len(diff_list)
else:
    decrease_avg = 0.00

cliq_tokens = {
    "client_id": config["CLIQ_CLIENT_ID"],
    "client_secret": config["CLIQ_CLIENT_SECRET"],
    "refresh_token": config["CLIQ_REFRESH_TOKEN"],
    "access_token": config["CLIQ_ACCESS_TOKEN"]
}

cliq = CliqClient(cliq_tokens)

if len(increased) > 0 or len(decreased) > 0:
    print("Increased:", len(increased))
    fr = FeedReport("Price_report-test.xlsx")
    fr.write_prices(increased, "increased", today_feed)
    print("Decreased:", len(decreased))
    fr.write_prices(decreased, "decreased", today_feed)
    print("No change:", unchanged)

    report_rows = [
        ["Increased:", len(increased), "(Avg: £" + str(increase_avg) + ")"],
        ["Decreased:", len(decreased), "(Avg: £" + str(decrease_avg) + ")"],
        ["unchanged:", unchanged],
    ]

    fr.write_report_sheet(report_rows, f"Report-{today}")

    params = {
        "filename": f"Uropa_price_report-{today}",
        "parent_id": config["WD_FOLDER_ID"],
        "override-name-exist": False
    }
    data = {
        "content": open(fr.filename, 'rb')
    }
    response = wd.query("/api/v1/upload", p=params, file=data)
    link = response["data"][0]["attributes"]["Permalink"]

    # post card with table to cliq
    chat_name = "itgroup"
    card_text = f"RB Price Report for {today}"
    card_title = "RB Price Report"
    thumbnail = "https://media.nisbets.com/images/theme/uropa/logo/uropa-logo.svg"
    table_title = "Detected Changes"
    table_hdrs = ["Change", "Count", "Avg Diff"]
    table_rws = [
        {
            "Change": "Increase",
            "Count": len(increased),
            "Avg Diff": increase_avg
        }, {
            "Change": "Decrease",
            "Count": len(decreased), 
            "Avg Diff": decrease_avg
        }, {
            "Change": "No Change",
            "Count": unchanged,
            "Avg Diff": "-"
        }
    ]
    btns = [{
        "label": "View Report",
        "type": "+",
        "action": {
            "type": "open.url",
            "data": {
                "web": link
            }
        }
    }]

    response = cliq.postInlineCard(chat_name, card_text, card_title, thumbnail, table_title, table_hdrs, table_rws, btns)
    print(response)

else:
    response = cliq.postSimpleMessage("itgroup", f"RB Price Report For {today}: No changes detected.")
    print(response)
