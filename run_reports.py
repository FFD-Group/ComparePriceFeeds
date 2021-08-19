from datetime import datetime
from pentland_stock_changes import PentlandStockChanges

pentland_stock = PentlandStockChanges("Pentland")

now = datetime.now()
print("Starting check at", now.strftime("%d-%m-%Y %H:%M:%S"))
print("Checking Pentland Stock...")
pentland_stock.run()
finished_time = datetime.now()
print("Finished check at", finished_time.strftime("%d-%m-%Y %H:%M:%S"))
print("----------------------------------------------------------------")