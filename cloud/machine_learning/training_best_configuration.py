import os
import warnings

import pandas as pd
from timeit import default_timer as timer
from sklearn.feature_selection import SelectKBest, mutual_info_classif

from machine_learning.classifier import best_classifier
from machine_learning.balancer import svm_smote
from machine_learning.scaler import delete_outliers, max_abs_scaler

from joblib import dump

from database.query import connect

warnings.simplefilter("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

n_feat = 6


def fill_na(training, testing, features):
    """Substitutes missing values with the mean value calculated only in training set for each feature

    Args:
        training: training set
        testing: testing set

    Returns:
        training set without missing values
    """
    for feat in features:
        feature_mean = training[feat].mean()
        training[feat] = training[feat].fillna(feature_mean)
        if testing is not None:
            testing[feat] = testing[feat].fillna(feature_mean)
    return training, testing


def main():
    db = connect('Cloud')
    cursor = db.cursor()
    cursor.execute('SELECT glucose, bloodPressure, insulin, bmi, skin, age, outcome FROM measurements LIMIT 50000')
    table_rows = cursor.fetchall()
    print(table_rows)
    cursor.close()
    db.close()

    training = pd.DataFrame(table_rows)
    # training = training.reset_index()
    # training = training.drop(['Index'], axis=1)
    # training.columns = range(len(training.columns))
    # training.reset_index(drop=True, inplace=False)
    # training.set_index('0', inplace=True)
    training = training.rename_axis(None)
    print(training.shape)

    # fill missing values
    training, _ = fill_na(training, None, training.columns.tolist()[:n_feat])

    # delete outliers
    training = delete_outliers(training)

    train_x = training.iloc[:, 0:n_feat].values
    train_y = training.iloc[:, n_feat].values

    # scaling data
    train_x, _ = max_abs_scaler(train_x, None)

    # balancing data
    train_x, train_y = svm_smote(train_x, train_y)

    # features selection
    k_best = SelectKBest(mutual_info_classif, k=6)
    train_x = k_best.fit_transform(train_x, train_y)

    start_classifier = timer()

    best_classifier_ = best_classifier(train_x, train_y, n_folds=5, metric='f1_macro')

    print("Elapsed time: ", timer() - start_classifier)

    dump(best_classifier_.best_estimator_, 'best_classifier.joblib')


if __name__ == "__main__":
    main()
