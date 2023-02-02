
from .imports import *

MODELS_PATH = '../../models/'

def inference(data_point_features):
    model = joblib.load(MODELS_PATH+'lgbm_optim.joblib')
    inference_results = model.predict_proba(data_point_features)
    inference_results_df_probas= pd.DataFrame(data=inference_results,columns=['Purchase','Not Purchase'])
    inference_label = 1 if np.amax(inference_results)>=0.5 else 0
    text_out = None
    if inference_label == 1:
        text_out = "Customer is {:.2f}% likely to purchase in the coming 1 month".format(np.amax(inference_results)*100)
    elif inference_label == 0:
        text_out = "Customer is {:.2f}% unlikely to purchase in the coming 1 month".format(np.amax(inference_results)*100)
    else:
        text_out = -1
    return inference_results, inference_results_df_probas, inference_label, text_out


