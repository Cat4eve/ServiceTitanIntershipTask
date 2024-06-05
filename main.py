from data_extractor import DataExtractor

if __name__ == '__main__':
    D = DataExtractor()
    arr = D._load_dataset('invoices_new.pkl')
    D._load_expired_list('expired_invoices.txt')
    D._transform_to_flat_data()
