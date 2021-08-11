from numpy import dtype
import pandas as pd

class Feed:

    def __init__(self, filename: str):
        self.filename = filename
        self.data = None
        self.rows = 0

    def loadToDataFrame(self):
        self.data = pd.read_csv(self.filename, dtype=str)
        self.rows = len(self.data.index)

    def __str__(self):
        return f"Feed from file: '{self.filename}' with {self.rows} rows of data."

    def get_product_data(self, product_code: str, column_label: str, product_code_label:str="Product Code"):
        return self.data.loc[self.data[product_code_label] == product_code, column_label].tolist()

    def get_next_product(self, product_code_label:str="Product Code") -> str:
        for product_code in self.data[product_code_label].values:
            yield product_code

    __repr__ = __str__

if __name__ == "__main__":
    f = Feed("yesterday.csv.example")
    f.loadToDataFrame()
    print(f.get_product_data("19300201", "Stock Level"))
    print(f.get_product_data("19300201", "Stock Promise Date"))
    print(f.get_product_data("19300201", "DROPPEDLINE"))
    for product in f.get_next_product():
        print(product)
    print(f)