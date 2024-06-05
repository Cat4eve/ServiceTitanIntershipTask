import pickle
import pandas as pd
import numpy as np

class DataExtractor:
    
    # Initialization of the class
    def __init__(self) -> None:
        
        # Attribute for storing in data from pickle file
        self.extracted_data = None

        # Attribute for storing expired invoices
        self.expired_list = None

        # Conversion for invoice item types
        self.type_conversation = {0: 'Material', 1: 'Equipment', 2: 'Service', 3: 'Other'}
        self.word_to_num_map = {
            'O': 0,
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'sixteen': 16,
            'seventeen': 17,
            'eighteen': 18,
            'nineteen': 19,
            'twenty': 20,
        }
        
        


    # Loading of data from pickle file from given URL location.
    def _load_dataset(self, url) -> list:

        #find file and open it
        file = open(url, 'rb')

        # load data using pickle load method
        data = pickle.load(file)

        # save the last extracted data as a property named 'extracted_data'
        self.extracted_data = data

        # return the given data of type list
        return data
    
    
    def _load_expired_list(self, url) -> list:
        # open file and read it
        file = open(url, 'r')

        # contain ids from single line
        string_line = file.readline()

        # separate by commas
        list_of_expired = string_line.split(', ')

        # replace strings by integers
        for index, item in enumerate(list_of_expired):
            list_of_expired[index] = int(item)

        # save as 'expired_list' attribute
        self.expired_list = list_of_expired

        # return value
        return list_of_expired
        
        

    # Transformation of data from s
    def _transform_to_flat_data(self) -> None:
        dictionary_to_be_convereted_to_dataframe = {'invoice_id': None,'created_on': None,'invoiceitem_id': None,
                                                    'invoiceitem_name': None,'type': None,'unit_price': None,'total_price': None,
                                                    'percentage_in_invoice': None,'is_expired': None}
        
        invoice_id_arr = []
        created_on_arr = []
        invoice_item_id_arr = []
        invoice_item_name_arr = []
        invoice_item_type_arr = []
        invoice_item_unit_price = []
        invoice_item_total_price = []
        is_expired_arr = []
        
        for item in self.extracted_data:
            if self._is_not_valid_date(item['created_on']):
                continue

            if ('items' not in item):
                continue
            
            for invoice_item in item['items']:
                print(invoice_item)
                if str(item['id'])[-1] == 'O':
                    invoice_id_integer = item['id'][:-1]
                else:
                    invoice_id_integer = item['id']

                invoice_id_arr.append(invoice_id_integer)
                created_on_arr.append(item['created_on'])
                invoice_item_id_arr.append(invoice_item['item']['id'])
                invoice_item_name_arr.append(invoice_item['item']['name'])
                if (self._is_not_valid_number(invoice_item['item']['type'])):
                    type = self.word_to_num_map[invoice_item['item']['type']]
                else:
                    type = int(invoice_item['item']['type'])
                invoice_item_type_arr.append(type)

                invoice_item_unit_price.append(int(invoice_item['item']['unit_price']))
                if (self._is_not_valid_number(invoice_item['quantity'])):
                    quantity = self.word_to_num_map[invoice_item['quantity']]
                else:
                    quantity = int(invoice_item['quantity'])
                invoice_item_total_price.append(int(invoice_item['item']['unit_price'])*quantity)

                # percentage_in_invoice.append(float())

                if invoice_id_integer in self.expired_list:
                    is_expired_arr.append(True)
                else:
                    is_expired_arr.append(False)

        
        full_price_per_invoice = []
        for i, item in enumerate(invoice_id_arr):
            sum = 0
            for index, element in enumerate(invoice_id_arr):
                if item == element:
                    sum += invoice_item_total_price[index]
            full_price_per_invoice.append(float(invoice_item_total_price[i]/sum))

        

        dictionary_to_be_convereted_to_dataframe['invoice_id'] = invoice_id_arr
        dictionary_to_be_convereted_to_dataframe['created_on'] = created_on_arr
        dictionary_to_be_convereted_to_dataframe['invoiceitem_id'] = invoice_item_id_arr
        dictionary_to_be_convereted_to_dataframe['invoiceitem_name'] = invoice_item_name_arr
        dictionary_to_be_convereted_to_dataframe['type'] = invoice_item_type_arr
        dictionary_to_be_convereted_to_dataframe['unit_price'] = invoice_item_unit_price
        dictionary_to_be_convereted_to_dataframe['total_price'] = invoice_item_total_price
        dictionary_to_be_convereted_to_dataframe['percentage_in_invoice'] = full_price_per_invoice
        dictionary_to_be_convereted_to_dataframe['is_expired'] = is_expired_arr

        data_frame = pd.DataFrame(data=dictionary_to_be_convereted_to_dataframe)

        data_frame['invoice_id'] = pd.to_numeric(data_frame['invoice_id'])
        data_frame['created_on'] = pd.to_datetime(data_frame['created_on'])

        data_frame = data_frame.sort_values(["invoice_id", "invoiceitem_id"], ascending=[True, True])

        data_frame.to_csv('Data_Extraction_Results.csv')
        return data_frame
    


    def _is_not_valid_date(self, date: str):
        try:
            np.datetime64(date)
            return False
        except ValueError:
            return True
        

    def _is_not_valid_number(self, number):
        try:
            int(number)
            return False
        except ValueError:
            return True