from feed import Feed
import pandas as pd
import xml.etree.ElementTree as ET

class XMLFeed(Feed):

    def __init__(self, filename: str):
        self.filename = filename
        self.data = None
        self.rows = 0

    def loadToDataFrame(self):
        xml_data = ET.parse(self.filename)
        xml = self.product_xml_to_dict(xml_data.getroot())
        self.data = pd.DataFrame.from_dict(xml, dtype=str)
        self.data = self.data.transpose()
        self.rows = len(self.data.index)

    def product_xml_to_dict(self, xml: ET.ElementTree, element_name="product") -> dict:
        d = dict()
        idx = 0
        for child in xml:
            if child.tag != element_name: continue
            product = dict()
            for tag in child:
                product[tag.tag] = tag.text
            d[idx] = product
            idx += 1
        return d

    def __str__(self):
        return f"XML Feed from local file '{self.filename}' with {self.rows} rows of data."

    __repr__ = __str__

if __name__ == "__main__":
    f = XMLFeed("Pentland-Stock-Test.xml")
    f.loadToDataFrame()
    print(f.data.head())
    print(f.get_product_data("ALEX2", "stockLevel", product_code_label="productCode"))
    print(f.get_product_data("Z6-1706D", "productName", product_code_label="productCode"))
    # for product in f.get_next_product(product_code_label="productCode"):
    #     print(product)
    print(f)