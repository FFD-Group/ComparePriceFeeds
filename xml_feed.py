from feed import Feed
import pandas as pd
import xml.etree.ElementTree as ET

class XMLFeed(Feed):
    '''
    A Feed class to enable operations on data from an XML file.
    '''

    def __init__(self, filename: str):
        '''
        Create a new XML Feed from an XML file.
        @params filename        The name of the local file to read.
        '''
        self.filename = filename
        self.data = None
        self.rows = 0

    def loadToDataFrame(self):
        '''
        Load the data from the file into a dataframe object.
        '''
        xml_data = ET.parse(self.filename)
        xml = self.product_xml_to_dict(xml_data.getroot())
        self.data = pd.DataFrame.from_dict(xml, dtype=str)
        self.data = self.data.transpose()
        self.rows = len(self.data.index)

    def product_xml_to_dict(self, xml: ET.ElementTree, element_name="product") -> dict:
        '''
        Parse the given-named XML elements into a dictionary.
        @param xml              The parsed ElementTree object from the file.
        @param element_name     The name of the elements to extract.
        @return dict            A dictionary of the extracted data.
        '''
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