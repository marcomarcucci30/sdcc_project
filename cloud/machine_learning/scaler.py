import sklearn.preprocessing as preprocessing
import numpy as np
from scipy import stats


def minMaxScaler(train_x, test_x):
    """Scaling data using minMaxScaler fitting only on train_x

    Args:
        train_x: Training set without Class Target
        test_x: Testing set without Class Target

    Returns: scaled train_x, test_x

    """
    scaler_x = preprocessing.MinMaxScaler(feature_range=(0, 1))
    scaler_x.fit(train_x)
    train_x = scaler_x.transform(train_x)
    test_x = scaler_x.transform(test_x)
    return train_x, test_x


def robustScale(train_x, test_x):
    """Scaling data using RobustScaler fitting only on train_x

    Args:
        train_x: Training set without Class Target
        test_x: Testing set without Class Target

    Returns: scaled train_x, test_x

    """
    scaler = preprocessing.RobustScaler()
    scaler.fit(train_x)
    train_x = scaler.transform(train_x)
    test_x = scaler.transform(test_x)
    return train_x, test_x


def max_abs_scaler(train_x, test_x):
    """Scaling data using MaxAbsScaler fitting only on train_x

    Args:
        train_x: Training set without Class Target
        test_x: Testing set without Class Target

    Returns: scaled train_x, test_x

    """
    scaler = preprocessing.MaxAbsScaler()
    scaler.fit(train_x)
    train_x = scaler.transform(train_x)
    if test_x is not None:
        test_x = scaler.transform(test_x)
    return train_x, test_x


def standard_scaler(train_x, test_x):
    """Scaling data using StandardScaler fitting only on train_x

    Args:
        train_x: Training set without Class Target
        test_x: Testing set without Class Target

    Returns: scaled train_x, test_x

    """
    scaler = preprocessing.StandardScaler()
    scaler.fit(train_x)
    train_x = scaler.transform(train_x).astype(float)
    if test_x is not None:
        test_x = scaler.transform(test_x).astype(float)

    return train_x, test_x

def delete_outliers(dataset):
    """Delete Outliers from dataset

    Args:
        dataset: dataset with outliers

    Returns: dataset without outliers

    """
    z_scores = stats.zscore(dataset)
    abs_z_scores = np.abs(z_scores)
    filtered_entries = (abs_z_scores < 3).all(axis=1)
    dataset = dataset[filtered_entries]
    return dataset
