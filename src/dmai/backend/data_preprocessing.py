
from .imports import *
import os

class DataPreprocessing(object):

    def load_data(self, data):
        """ Method to load data from json file"""
        df = None
        if os.path.isdir(data) or os.path.isfile(data):
            if str(data).split('.')[-1]=='json':
                df = pd.read_json(data,orient='records')
            
            elif str(data).split('.')[-1]=='xlsx':
                df = pd.read_excel(data)

            elif str(data).split('.')[-1]=='csv':
                df = pd.read_csv(data)
            else:
                format_message="Unsupported file format";
                return format_message
        else:
                format_message="Pass a data file";
                return format_message
        return df

    def drop_nan(self, data):
        """Method that takes in a text and removes all null values."""
        return data.dropna(how='all').reset_index(drop=True)

    def drop_duplicates(self, data):
        """Method that takes in a text and removes all null values."""
        return data.drop_duplicates(keep='last').reset_index(drop=True)

    def string_to_date(self, data, column='paid_at'):
        """Method that converts date to string datetime."""
        data[column] = pd.to_datetime(data[column])
        return  data

    def string_to_date(self, data, column='paid_at'):
        """Method that converts date to string datetime."""
        data[column] = pd.to_datetime(data[column])
        return  data

    def previous_data(self, data,from_date, to_date, column='paid_at'):
        """Method that return purchase behaviour for last defined time period."""
        return data[(data[column] < to_date) & (data[column] >= from_date)].reset_index(drop=True)

    def next_data(self, data,column, from_date, to_date):
        """Method that returns the next data for check first purchase after the last time."""
        return data[(data[column] >= from_date) & (data[column] < to_date)].reset_index(drop=True)

    def get_customers(self, data, column='customer_id'):
        """filter unique customer who did purchase in previous 9 months."""
        customers = pd.DataFrame(data[column].unique())
        customers.columns = [column]
        return customers
    
    def get_last_purchase(self, previous_data, column='customer_id'):
        """create a dataframe with customer id and last purchase date in invoices_next."""
        last_purchase =previous_data.groupby(column).paid_at.max().reset_index()
        last_purchase.columns = [column,'max_purchase_date']
        return last_purchase

    def get_next_first_purchase(self, next_data, column='customer_id'):
        """create a dataframe with customer id and first purchase date in next"""
        next_first_purchase = next_data.groupby('customer_id').paid_at.min().reset_index()
        next_first_purchase.columns = ['customer_id','min_purchase_date']
        return next_first_purchase
        
    def join_last_first_purchases(self, last_purchase, next_first_purchase, column='customer_id'):
        """merge two dataframes [last purchase and first purchase]"""
        return pd.merge(last_purchase,next_first_purchase,on=column,how='left')

    def get_time_difference_between_purchases(self, purchases):
        """calculate the time difference in days:"""
        purchases['next_purchase_day'] = (purchases['min_purchase_date'] - purchases['max_purchase_date']).dt.days
        return purchases 

    def assign_time_difference_to_customers(self, customers, time_difference):
        """ merge time difference with customers"""
        customers_time_difference = pd.merge(customers, time_difference[['customer_id','next_purchase_day']],on='customer_id',how='left')
        return customers_time_difference
    