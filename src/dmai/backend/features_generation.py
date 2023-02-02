from .imports import *
# #### Features Engineering

MODELS_PATH = '../../models/'

class FeaturesGeneration():

    def recency(self, data_point_previous, data_point_customer_previous):
        #get max purchase date for Recency and create a dataframe of the last purchase before cut off date
        invoices_max_purchase = data_point_previous.groupby('customer_id').paid_at.max().reset_index()
        invoices_max_purchase.columns = ['customer_id','max_purchase_date']

        #find the recency in days and add it to invoices_customers, given as the day difference between the last purchase before cut off, and other purchases before cut of
        invoices_max_purchase['Recency'] = (invoices_max_purchase['max_purchase_date'].max() - invoices_max_purchase['max_purchase_date']).dt.days
        data_point_customer_previous = pd.merge(data_point_customer_previous, invoices_max_purchase[['customer_id','Recency']], on='customer_id')

        return data_point_customer_previous

    def recency_cluster(self, data_point_customer_previous):
        #clustering for Recency, use elbow method to determine the number of clusters
        import joblib
        kmeans_recency = joblib.load(MODELS_PATH+'kmeans_recency.joblib')
        data_point_customer_previous['RecencyCluster'] = kmeans_recency.predict(data_point_customer_previous[['Recency']])
        return data_point_customer_previous

    def frequency(self, data_point_previous, data_point_customer_previous):
        #get total purchases for frequency scores
        invoices_frequency = data_point_previous.groupby('customer_id').paid_at.count().reset_index()
        invoices_frequency.columns = ['customer_id','Frequency']
        #add frequency column to invoices_customers
        data_point_customer_previous = pd.merge(data_point_customer_previous, invoices_frequency, on='customer_id')
        return data_point_customer_previous

    def frequency_cluster(self,data_point_customer_previous):
        #clustering for frequency
        import joblib
        kmeans_frequency = joblib.load(MODELS_PATH+'kmeans_frequency.joblib')
        data_point_customer_previous['FrequencyCluster'] = kmeans_frequency.predict(data_point_customer_previous[['Frequency']])
        return data_point_customer_previous

    def monetary_value(self,data_point_previous, data_point_customer_previous):
        #calculate monetary value, create a dataframe with it
        data_point_previous['Revenue'] = data_point_previous['amount'] *data_point_previous['items_count']
        invoices_revenue = data_point_previous.groupby('customer_id').Revenue.sum().reset_index()
        #add Revenue column to invoices_customers
        data_point_customer_previous = pd.merge(data_point_customer_previous, invoices_revenue, on='customer_id')
        return data_point_customer_previous

    def revenue_cluster(self,data_point_customer_previous):
        #Revenue clusters 
        import joblib
        kmeans_revenue = joblib.load(MODELS_PATH+'kmeans_revenue.joblib')
        data_point_customer_previous['RevenueCluster'] = kmeans_revenue.predict(data_point_customer_previous[['Revenue']])
        return data_point_customer_previous

    def overall_score(self, data_point_customer_previous):
        #building overall segmentation
         data_point_customer_previous['OverallScore'] =  data_point_customer_previous['RecencyCluster'] +  data_point_customer_previous['FrequencyCluster'] +  data_point_customer_previous['RevenueCluster']
         return  data_point_customer_previous

    def segments(self, data_point_customer_previous):
        #assign segment names
        data_point_customer_previous['Segment'] = 'Low-Value'
        data_point_customer_previous.loc[data_point_customer_previous['OverallScore']>2,'Segment'] = 'Mid-Value' 
        data_point_customer_previous.loc[data_point_customer_previous['OverallScore']>4,'Segment'] = 'High-Value' 
        return data_point_customer_previous

    def trace_back_three(self, data_point_previous, data_point_customer_previous):
        #create a dataframe with customer_id and Invoice Date
        invoices_day_order = data_point_previous[['customer_id','paid_at']]
        #convert Invoice Datetime to day
        invoices_day_order['InvoiceDay'] = data_point_previous['paid_at'].dt.date
        invoices_day_order = invoices_day_order.sort_values(['customer_id','paid_at'])
        #drop duplicates
        invoices_day_order = invoices_day_order.drop_duplicates(subset=['customer_id','InvoiceDay'],keep='first')
        #shifting last 3 purchase dates
        invoices_day_order['PrevInvoiceDate'] = invoices_day_order.groupby('customer_id')['InvoiceDay'].shift(1)
        invoices_day_order['T2InvoiceDate'] = invoices_day_order.groupby('customer_id')['InvoiceDay'].shift(2)
        invoices_day_order['T3InvoiceDate'] = invoices_day_order.groupby('customer_id')['InvoiceDay'].shift(3)
        #calculate the day differences between purchases (the 3 purchases gaps)
        invoices_day_order['DayDiff'] = (invoices_day_order['InvoiceDay'] - invoices_day_order['PrevInvoiceDate']).dt.days
        invoices_day_order['DayDiff2'] = (invoices_day_order['InvoiceDay'] - invoices_day_order['T2InvoiceDate']).dt.days
        invoices_day_order['DayDiff3'] = (invoices_day_order['InvoiceDay'] - invoices_day_order['T3InvoiceDate']).dt.days
        #find the mean day difference , and std 
        invoices_day_diff = invoices_day_order.groupby('customer_id').agg({'DayDiff': ['mean','std']}).reset_index()
        invoices_day_diff.columns = ['customer_id', 'DayDiffMean','DayDiffStd']
        ##we have customers who purchased only one time, We can't keep customer who has purchased one time, for this case we keep customer who has purchased atleast 3 times
        invoices_day_order_last = invoices_day_order.drop_duplicates(subset=['customer_id'],keep='last') # filter with one purchase

        invoices_day_order_last = invoices_day_order_last.dropna()
        invoices_day_order_last = pd.merge(invoices_day_order_last, invoices_day_diff, on='customer_id')
        data_point_customer_previous = pd.merge(data_point_customer_previous, invoices_day_order_last[['customer_id','DayDiff','DayDiff2','DayDiff3','DayDiffMean','DayDiffStd']], on='customer_id')
        return data_point_customer_previous

    def dummy_data(self, data_point_customer_previous):
        #create invoices_class as a copy of invoices_customers before applying get_dummies
        invoices_class = data_point_customer_previous.copy()
        invoices_class = pd.get_dummies(invoices_class)
        # drop less importand columns as per trining
        features_generated  = invoices_class.drop(['DayDiff', 'DayDiff3', 'DayDiff2', 'Recency', 'DayDiffMean','DayDiffStd'], axis=1)
        return features_generated


    #create a class for numerical data tansformation
class Transform(TransformerMixin,BaseEstimator):
    def fit(self,X,y=None):
        return self
    def transform(self,X,y=0):
        num_pipeline = Pipeline([('scaler',StandardScaler())])
        X = num_pipeline.fit_transform(X)
        return pd.DataFrame(X)
