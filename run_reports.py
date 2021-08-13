from pentland_stock_changes import PentlandStockChanges
from rb_price_changes import RBPriceChanges
from rb_stock_changes import RBStockChanges

pentland_stock = PentlandStockChanges("Pentland")
rb_prices = RBPriceChanges()
rb_stock = RBStockChanges("RBStock")

print("Checking RB Stock...")
rb_stock.run()
print("Checking RB Prices...")
rb_prices.run()
print("Checking Pentland Stock...")
pentland_stock.run()