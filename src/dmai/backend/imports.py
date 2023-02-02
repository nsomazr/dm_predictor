#import all the necessary libraries
import joblib
import pandas as pd 
import numpy as np 
from datetime import datetime 
from warnings import simplefilter
import json
from sklearn.base import (TransformerMixin, BaseEstimator)
from sklearn.pipeline import ( FeatureUnion, Pipeline )
from sklearn.preprocessing import StandardScaler 
simplefilter(action='ignore', category=FutureWarning)