from datetime import datetime
from rb_price_changes import RBPriceChanges

rb_prices = RBPriceChanges()

now = datetime.now()
print("Starting check at", now.strftime("%d-%m-%Y %H:%M:%S"))
print("Checking RB Prices...")
rb_prices.run()
finished_time = datetime.now()
print("Finished check at", finished_time.strftime("%d-%m-%Y %H:%M:%S"))