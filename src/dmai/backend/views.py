from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Inference
from .serializers import InferenceModelSerializer, DataAPTModelSerializer
from .data_preprocessing import DataPreprocessing
from .features_generation import FeaturesGeneration, Transform
from .imports import *
from .forms import DataForm
from .inference import *
from .models import DataAPI, Data
import string
import random
import os
# Create your views here.

min_rows = 20

class DataInferenceAPIView(APIView):

    def get(self, request):
        inference = DataAPI.objects.all()
        serializer = DataAPTModelSerializer(inference, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        for data in request.data:
            data['processed_at'] = "2023-02-02 10:38:06"
        serializer = DataAPTModelSerializer(data = request.data, many = True)

        if serializer.is_valid():
            
            serializer.save()
            
            data_preprocessor = DataPreprocessing()

            BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath(__file__)))

            file_path = os.path.join(BASE_DIR,'media/data/customer_')+str(request.data[0].get('customer_id'))+'.json'

            with open(file_path, "w") as outfile:
                   json.dump(request.data, outfile)

            data_point = data_preprocessor.load_data(file_path)

            if data_point.shape[0] >= min_rows:

                # print(data_point.info())

                # #### Data Preprocessing
                data_point = data_preprocessor.drop_nan(data_point)

                # data_point['paid_at'] = data_point["paid_at"].values.astype(str)

                # print("After", data_point.info())

                #convert date field from string to datetime
                data_point = data_preprocessor.string_to_date(data_point,'paid_at')

                #choose 30 November as a cutt of date (1, Jan - 30 November) for behaviour data
                data_point_previous = data_preprocessor.previous_data(data = data_point, from_date = datetime(2022,1,1,00,00,00), to_date= datetime(2022,11,30,23,59,00))

                # data after cut off date (1 month window), to check for next purchase
                data_point_next = data_preprocessor.previous_data(data = data_point, from_date = datetime(2022,11,30,23,59,00), to_date= datetime(2022,12,31,23,59,0))

                #filter unique customer who did purchase in previous 9 months
                data_point_customer_previous = data_preprocessor.get_customers(data_point_previous, column='customer_id')

                #create a dataframe with customer id and last purchase date in invoices_previous
                last_purchase_data_point = data_preprocessor.get_last_purchase(data_point_previous, column='customer_id')

                #create a dataframe with customer id and first purchase date in next
                next_first_purchase_data_point = data_preprocessor.get_next_first_purchase(data_point_next, column='customer_id')

                #merge two dataframes [last purchase and first purchase]
                purchase_dates = data_preprocessor.join_last_first_purchases(last_purchase_data_point, next_first_purchase_data_point, column='customer_id' )

                #calculate the time difference in days:
                purchase_dates = data_preprocessor.get_time_difference_between_purchases(purchases=purchase_dates)

                features_generator = FeaturesGeneration()

                # Add recency feature 
                data_point_customer_previous = features_generator.recency(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                # Add recency cluster
                data_point_customer_previous = features_generator.recency_cluster(data_point_customer_previous=data_point_customer_previous)

                # Add frequency
                data_point_customer_previous = features_generator.frequency(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                # add frequency cluster
                data_point_customer_previous = features_generator.frequency_cluster(data_point_customer_previous=data_point_customer_previous)

                # Add Money value
                data_point_customer_previous = features_generator.monetary_value(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                #add money cluster
                data_point_customer_previous = features_generator.revenue_cluster(data_point_customer_previous=data_point_customer_previous)

                # add overall score
                data_point_customer_previous = features_generator.overall_score(data_point_customer_previous=data_point_customer_previous)

                # add segments
                data_point_customer_previous = features_generator.segments(data_point_customer_previous=data_point_customer_previous)

                # Add trace back tree purchases
                data_point_customer_previous = features_generator.trace_back_three(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                # add segments
                data_point_customer_previous_features = features_generator.dummy_data(data_point_customer_previous=data_point_customer_previous)

                transform =  Transform()

                data_point_customer_previous_features = transform.fit_transform(data_point_customer_previous_features)

                inference_results,inference_results_df_probas,inference_label,inference_text = inference(data_point_customer_previous_features)  

                customer_id = request.data[0].get('customer_id')

                new_inference = Inference(customer_id=customer_id, inference_label=inference_label, inference_text=inference_text, inference_results=inference_results_df_probas)

                new_inference.save()

                return Response({'inference_label':inference_label, 'inference_probas':inference_results_df_probas, 'text':inference_text}, status = 201)
            else:
                return Response("Minimum observations suported is 20. Increase your observations.", status = 201)
        return Response(serializer.errors, status = 400)

class InferenceAPIView(APIView):

    def get(self, request):
        inference_results = Inference.objects.all()
        serializer = InferenceModelSerializer(inference_results, many = True)
        return Response(serializer.data)
    

def prediction(request):

    if request.method == 'POST' and request.FILES['filename']:

        data_form = DataForm(request.POST,request.FILES)

        if data_form.is_valid():

            file_path = request.FILES['filename']

            file_name = file_path.name

            file_name = str(file_name)

            file_name = file_name.split('/')[-1].split('.')[-2]

            txt = 'UI'.join(random.choices(string.ascii_uppercase + string.digits, k = 5))    

            id = txt+str(np.random.randint((1000, 1000000)))

            new_file = Data(id =id, filepath=file_path, filename=file_name)

            new_file.save()

            data_selected = Data.objects.get(id=id)

            data_path = data_selected.filepath

            data_preprocessor = DataPreprocessing()

            data_point = data_preprocessor.load_data(str(data_path))

            if type(data_point) == str:

                format_message = data_point

                return render(request,template_name='pages/index.html', context={'data_form':data_form, 'format_message':format_message})

            else:

                if data_point.shape[0] >= min_rows:

                    # #### Data Preprocessing
                    data_point = data_preprocessor.drop_nan(data_point)

                    #convert date field from string to datetime
                    data_point = data_preprocessor.string_to_date(data_point,'paid_at')

                    #choose 30 November as a cutt of date (1, Jan - 30 November) for behaviour data
                    data_point_previous = data_preprocessor.previous_data(data = data_point, from_date = datetime(2022,1,1,00,00,00), to_date= datetime(2022,11,30,23,59,00))

                    # data after cut off date (1 month window), to check for next purchase
                    data_point_next = data_preprocessor.previous_data(data = data_point, from_date = datetime(2022,11,30,23,59,00), to_date= datetime(2022,12,31,23,59,0))

                    #filter unique customer who did purchase in previous 9 months
                    data_point_customer_previous = data_preprocessor.get_customers(data_point_previous, column='customer_id')

                    #create a dataframe with customer id and last purchase date in invoices_previous
                    last_purchase_data_point = data_preprocessor.get_last_purchase(data_point_previous, column='customer_id')

                    #create a dataframe with customer id and first purchase date in next
                    next_first_purchase_data_point = data_preprocessor.get_next_first_purchase(data_point_next, column='customer_id')

                    #merge two dataframes [last purchase and first purchase]
                    purchase_dates = data_preprocessor.join_last_first_purchases(last_purchase_data_point, next_first_purchase_data_point, column='customer_id' )

                    #calculate the time difference in days:
                    purchase_dates = data_preprocessor.get_time_difference_between_purchases(purchases=purchase_dates)

                    features_generator = FeaturesGeneration()

                    # Add recency feature 
                    data_point_customer_previous = features_generator.recency(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                    # Add recency cluster
                    data_point_customer_previous = features_generator.recency_cluster(data_point_customer_previous=data_point_customer_previous)

                    # Add frequency
                    data_point_customer_previous = features_generator.frequency(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                    # add frequency cluster
                    data_point_customer_previous = features_generator.frequency_cluster(data_point_customer_previous=data_point_customer_previous)

                    # Add Money value
                    data_point_customer_previous = features_generator.monetary_value(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                    #add money cluster
                    data_point_customer_previous = features_generator.revenue_cluster(data_point_customer_previous=data_point_customer_previous)

                    # add overall score
                    data_point_customer_previous = features_generator.overall_score(data_point_customer_previous=data_point_customer_previous)

                    # add segments
                    data_point_customer_previous = features_generator.segments(data_point_customer_previous=data_point_customer_previous)

                    # Add trace back tree purchases
                    data_point_customer_previous = features_generator.trace_back_three(data_point_previous=data_point_previous, data_point_customer_previous=data_point_customer_previous)

                    # add segments
                    data_point_customer_previous_features = features_generator.dummy_data(data_point_customer_previous=data_point_customer_previous)

                    transform =  Transform()

                    data_point_customer_previous_features = transform.fit_transform(data_point_customer_previous_features)

                    inference_results,inference_results_df_probas,inference_label,inference_text = inference(data_point_customer_previous_features)

                    context = {'data_form':data_form, 'inference_label': inference_label,'inference_text':inference_text }

                    return render(request,template_name='pages/index.html', context=context)
                else:
                    format_message = "Minimum observations suported is 20. Increase your observations"
                    return render(request,template_name='pages/index.html', context={'data_form':data_form, 'format_message':format_message})
        else:
            return render(request,template_name='pages/index.html', context={'data_form':data_form})
