from datetime import datetime
from interlevin_stock_changes import InterlevinStockChanges

interlevin_stock = InterlevinStockChanges("Interlevin")

now = datetime.now()
print("Starting check at", now.strftime("%d-%m-%Y %H:%M:%S"))
print("Checking Interlevin Stock...")
interlevin_stock.run()
finished_time = datetime.now()
print("Finished check at", finished_time.strftime("%d-%m-%Y %H:%M:%S"))
print("--------------------------------------------------------------")

'''
Sample of Interlevin XML feed (19th Aug 2021):

Stock due value: <Stock>&#9742; stock due</Stock>
In stock value:  <Stock>✓ in stock</Stock>

<CatalogueExport>
    <Product>
        <CustomerType/>
        <Category>Commercial Glass Lid Chest Freezers</Category>
        <Sub_Cat_1/>
        <Sub_Cat_2/>
        <Product_Code>1100CHV WH</Product_Code>
        <Temperature_Range>-18/-24</Temperature_Range>
        <Refrigerant>R290</Refrigerant>
        <Defrost>Manual</Defrost>
        <Shelves/>
        <Int_Finish>White</Int_Finish>
        <Ext_Finish>White</Ext_Finish>
        <Power>13 Amp</Power>
        <kWh_x002F_24hr>4.90</kWh_x002F_24hr>
        <Watts>411</Watts>
        <Noise_Level_dB>48</Noise_Level_dB>
        <Max_Ambient>25°C at 60% RH</Max_Ambient>
        <Reversible_Door/>
        <Climate_Class>3</Climate_Class>
        <Ext_H>780</Ext_H>
        <Ext_W>2500</Ext_W>
        <Ext_D>960</Ext_D>
        <Weight_KG>125.0</Weight_KG>
        <Int_H>620</Int_H>
        <Int_W>1135</Int_W>
        <Int_D>790</Int_D>
        <Pack_H>840</Pack_H>
        <Pack_W>2590</Pack_W>
        <Pack_D>1030</Pack_D>
        <Packed_Weight_KG>200.0</Packed_Weight_KG>
        <Diagram_Caption/>
        <PDF_Page_No/>
        <Catalogue_Supplier_Name>Arcaboa</Catalogue_Supplier_Name>
        <Next_Day_Delivery>N</Next_Day_Delivery>
        <Delivery_Group>4</Delivery_Group>
        <Special_Installation>No</Special_Installation>
        <Site_Survey>No</Site_Survey>
        <Net_Price/>
        <Net_Service_Price>0.00</Net_Service_Price>
        <Net_Service_Price_2>0.00</Net_Service_Price_2>
        <Special_Offer_Price>0.00</Special_Offer_Price>
        <New>No</New>
        <Amps>3.1</Amps>
        <Energy_Efficiency_Class/>
        <Energy_Class_Image/>
        <kWh_annum>1,789</kWh_annum>
        <Net_Volume/>
        <GTIN_EAN_Number/>
        <Stock>☎ stock due</Stock>
        <Due_Date/>
        <Unpack_and_Position>42.00</Unpack_and_Position>
        <Remove_and_Dispose>105.00</Remove_and_Dispose>
        <Baskets>0</Baskets>
        <Max_No_of_Baskets>8</Max_No_of_Baskets>
        <Range_Title>CHV Range</Range_Title>
        <Thumbnail/>
        <Image>https://www.interlevin.co.uk/images/product/960.jpg</Image>
        <Packed_Image/>
        <Diagram/>
        <PL1_Price>1,956.00</PL1_Price>
        <SP1_Price>0.00</SP1_Price>
        <RRP>1,956.00</RRP>
        <Capacity_Ltr>1032</Capacity_Ltr>
        <Capacity_Cuft>36.4</Capacity_Cuft>
        <Features>*Flat sliding lids*Static cooling*Adjustable feet*Temperature display*Defrost drain*Low maintenance condensor*Bumper bars1100CHV has a central partition*Twin controllers on 1100CHV</Features>
        <Comments_Notes/>
        <Image_Caption>1100CHV</Image_Caption>
        <Order/>
        <Product_Title>1100CHV WH</Product_Title>
        <Sub_Title>Island Site Freezer</Sub_Title>
        <Product_Price_Description/>
        <Refrigerant_Charge>2 x 95</Refrigerant_Charge>
        <Sales_Description/>
    </Product>
......
......


'''