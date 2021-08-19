from feed import Feed

class FeedComparator:

    def __init__(self, f1: Feed, f2: Feed) -> None:
        self.f1 = f1
        self.f2 = f2

    def get_comparable_feed_values(self, product, value_col) -> tuple:
        if self.f1.data.empty:
            raise ValueError("Feed 1 does not have any data!")
        if self.f2.data.empty:
            raise ValueError("Feed 2 does not have any data!")

        feed1_val = self.f1.get_product_data(product, value_col)
        feed2_val = self.f1.get_product_data(product, value_col)

        return (feed1_val, feed2_val)

    def get_newly_oos_no_levels(self, stock_label: str="Stock Level", stock_value: str="✓ in stock"):
        if self.f1.data.empty:
            raise ValueError("Feed 1 does not have any data!")
        if self.f2.data.empty:
            raise ValueError("Feed 2 does not have any data!")
        
        newly_oos = list()
        for product in self.f1.get_next_product():
            product_current_stock = True if self.f1.get_product_data(product, stock_label)[0] == stock_value else False
            product_past_stock = True if self.f2.get_product_data(product, stock_label)[0] == stock_value else False
            if (product_current_stock == False and product_past_stock == True):
                stock_due = self.f1.get_product_data(product, stock_label)[0]
                stock_due = stock_due.replace("&#9742;", "")
                newly_oos.append((product, stock_due))
        
        return newly_oos

    def get_newly_oos(self, stock_label: str="Stock Level", check_dropped: bool=False, due_date: bool=False) -> list:
        if self.f1.data.empty:
            raise ValueError("Feed 1 does not have any data!")
        if self.f2.data.empty:
            raise ValueError("Feed 2 does not have any data!")

        newly_oos = list()
        for product in self.f1.get_next_product():
            product_current_stock = int(self.f1.get_product_data(product, stock_label)[0])
            product_past_stock = int(self.f2.get_product_data(product, stock_label)[0])
            if check_dropped:
                product_current_dropped = str(self.f1.get_product_data(product, "DROPPEDLINE")[0])
                if product_current_dropped != "Y":
                    if (product_current_stock == 0 and product_past_stock != 0):
                        if due_date:
                            stock_due = str(self.f1.get_product_data(product, "Stock Promise Date")[0])
                            newly_oos.append((product, stock_due))
                        else:
                            newly_oos.append(product)
            else:
                if (product_current_stock == 0 and product_past_stock != 0):
                    if due_date:
                        stock_due = self.f1.get_product_data(product, stock_label)
                        newly_oos.append((product, stock_due))
                    else:
                        newly_oos.append(product)

        return newly_oos

    def get_back_in_stock_no_levels(self, stock_label: str="Stock Level", stock_value: str="✓ in stock") -> list:
        if self.f1.data.empty:
            raise ValueError("Feed 1 does not have any data!")
        if self.f2.data.empty:
            raise ValueError("Feed 2 does not have any data!")

        newly_in = list()
        for product in self.f1.get_next_product():
            product_current_stock = True if self.f1.get_product_data(product, stock_label)[0] == stock_value else False
            product_past_stock = True if self.f2.get_product_data(product, stock_label)[0] == stock_value else False
            if (product_current_stock and not product_past_stock):
                stock_due = self.f1.get_product_data(product, "Stock Promise Date")[0]
                newly_in.append((product, product_current_stock))

        return newly_in

    def get_back_in_stock(self, stock_label: str="Stock Level") -> list:
        if self.f1.data.empty:
            raise ValueError("Feed 1 does not have any data!")
        if self.f2.data.empty:
            raise ValueError("Feed 2 does not have any data!")

        newly_in = list()
        for product in self.f1.get_next_product():
            product_current_stock = int(self.f1.get_product_data(product, stock_label)[0])
            product_past_stock = int(self.f2.get_product_data(product, stock_label)[0])
            if (product_current_stock != 0 and product_past_stock == 0):
                newly_in.append((product, product_current_stock))

        return newly_in

    def get_newly_dropped_lines(self) -> list:
        if self.f1.data.empty:
            raise ValueError("Feed 1 does not have any data!")
        if self.f2.data.empty:
            raise ValueError("Feed 2 does not have any data!")

        newly_dropped = list()
        for product in self.f1.get_next_product():
            product_current_dl = str(self.f1.get_product_data(product, "DROPPEDLINE")[0])
            product_past_dl = str(self.f2.get_product_data(product, "DROPPEDLINE")[0])
            if (product_current_dl == "Y" and product_past_dl != "Y"):
                newly_dropped.append(product)

        return newly_dropped
