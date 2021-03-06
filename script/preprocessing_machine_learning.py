# author: group 21
# date: 2020-11-27

"""A script that loads the training data frame and creates the preprocessor to use in the 
   machine learning pipeline

Usage: preprocessing_machine_learning.py --input_train=<input_train> --input_test=<input_test> --out_dir=<out_dir> 

Options:
--input_train=<input_train>          Path (including filename) to training data (feather file) used for the preprocessing
--input_test=<input_test>            Path (including filename) to the test data (feather file)
--out_dir=<out_dir>                  Path to directory where the results dataframes should be written
"""

from docopt import docopt
import pickle
import numpy as np
import os
import os.path
import feather
import pandas as pd
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.model_selection import (
    RandomizedSearchCV,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    PolynomialFeatures,
    StandardScaler,
)


opt = docopt(__doc__)

def main(input_train, input_test, out_dir):
  
  # read the train dataframe
  train_df = pd.read_feather(input_train)
  test_df = pd.read_feather(input_test)
  
  # remove the outliner
  mean_hours = train_df["Absenteeism time in hours"].mean()
  sd_hours = train_df["Absenteeism time in hours"].std()
  train_df = train_df[train_df["Absenteeism time in hours"] < mean_hours +3*sd_hours]
  
  # split train_df into X_train, y_train
  X_train, y_train = train_df.drop(columns = ["ID", "Absenteeism time in hours"]), train_df["Absenteeism time in hours"]
  X_test, y_test = test_df.drop(columns = ["ID", "Absenteeism time in hours"]), test_df["Absenteeism time in hours"]
  
  # save the X_train, y_train, X_test, y_test into feather files
  X_train_file = out_dir + "/X_train.pickle"
  
  pickle_out = open(X_train_file, "wb")
  pickle.dump(X_train, pickle_out)
  pickle_out.close()
  
      
  y_train_file = out_dir + "/y_train.pickle"
  
  pickle_out = open(y_train_file, "wb")
  pickle.dump(y_train, pickle_out)
  pickle_out.close()
  
  
  X_test_file = out_dir + "/X_test.pickle"
  
  pickle_out = open(X_test_file, "wb")
  pickle.dump(X_test, pickle_out)
  pickle_out.close()
      
      
  y_test_file = out_dir + "/y_test.pickle"
  
  pickle_out = open(y_test_file, "wb")
  pickle.dump(y_test, pickle_out)
  pickle_out.close()
  
  # create the features lists by type
  numeric_features = X_train.select_dtypes('number').drop(columns=["Body mass index", "Service time"]).columns.tolist()
  binary_features = X_train.select_dtypes('bool').drop(columns=["Disciplinary failure"]).columns.tolist()
  categorical_features = X_train.select_dtypes('category').drop(columns=["Education", "Month of absence"]).columns.tolist()
  ordinal_features =['Education']
  drop_features = ["Disciplinary failure", "Body mass index", "Service time", "Month of absence"]
  education_levels = [1,2,3,4]
  
  
  # carry out cross validation
  numeric_transformer = make_pipeline(StandardScaler())
  categorical_transformer = make_pipeline(OneHotEncoder(handle_unknown="ignore"))
  binary_transformer = make_pipeline(OneHotEncoder(drop="if_binary", dtype=int))
  ordinal_transformer = make_pipeline(OrdinalEncoder(categories=[education_levels], dtype=int))
  
  preprocessor = make_column_transformer(
    ("drop", drop_features),
    (numeric_transformer, numeric_features), 
    (categorical_transformer, categorical_features),
    (binary_transformer, binary_features),
    (ordinal_transformer, ordinal_features))
  
  
  # generate the feature list
  preprocessor.fit_transform(X_train)
  total_features = numeric_features + list(preprocessor.named_transformers_["pipeline-2"].named_steps["onehotencoder"].get_feature_names(categorical_features)) + binary_features + ordinal_features

  feature_list = out_dir + "/total_features.pickle"
  pickle_out = open(feature_list, "wb")
  pickle.dump(total_features, pickle_out)
  pickle_out.close()
  
  
  # save the result in a pickle file
  processor_file = out_dir + "/processor.pickle"

  pickle_out = open(processor_file,"wb")
  pickle.dump(preprocessor,pickle_out)
  pickle_out.close()
  
      
if __name__ == "__main__":
  main(opt["--input_train"], opt["--input_test"], opt["--out_dir"])
  
