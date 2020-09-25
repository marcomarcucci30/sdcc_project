from imblearn.over_sampling import SMOTE, SVMSMOTE, KMeansSMOTE, SMOTENC, RandomOverSampler, ADASYN
from imblearn.combine import SMOTETomek
from imblearn.under_sampling import NearMiss


def undersampling(X, y):
    """Balancing data using NearMiss

    Args:
        X: Training set without Class Target
        y:Training set Class Target

    Returns:
        balanced train_x, test_x
    """
    sample = NearMiss(version=1)
    X, y = sample.fit_resample(X, y)
    print('after balancing:', X.shape)
    return X, y


def adasyn(X, y):
    """Balancing data using ADASYN

    Args:
        X: Training set without Class Target
        y:Training set Class Target

    Returns:
        balanced train_x, test_x
    """
    sample = ADASYN(random_state=42, sampling_strategy='minority')
    X, y = sample.fit_resample(X, y)
    print('after balancing:', X.shape)
    return X, y


def svm_smote(X, y):
    """Balancing data using SVMSMOTE

    Args:
        X: Training set without Class Target
        y:Training set Class Target

    Returns:
        balanced train_x, test_x
    """
    sample = SVMSMOTE(random_state=42)
    X, y = sample.fit_resample(X, y)
    print('after balancing:', X.shape)
    return X, y


def smote(X, y):
    """Balancing data using SMOTE

    Args:
        X: Training set without Class Target
        y:Training set Class Target

    Returns:
        balanced train_x, test_x
    """
    sample = SMOTE(random_state=42, k_neighbors=5)
    X, y = sample.fit_resample(X, y)
    print('after balancing:', X.shape)
    return X, y


def smote_tomek(X, y):
    """Balancing data using SMOTETomek

    Args:
        X: Training set without Class Target
        y:Training set Class Target

    Returns:
        balanced train_x, test_x
    """
    sample = SMOTETomek(random_state=42, sampling_strategy='all')
    X, y = sample.fit_resample(X, y)
    print('after balancing:', X.shape)
    return X, y


def smote_nc(X, y):
    """Balancing data using SMOTENC

    Args:
        X: Training set without Class Target
        y:Training set Class Target

    Returns:
        balanced train_x, test_x
    """
    sample = SMOTENC(categorical_features=[0, 1], random_state=42)
    X, y = sample.fit_resample(X, y)
    print('after balancing:', X.shape)
    return X, y


def over_sample(X, y):
    """Balancing data using RandomOverSampler

    Args:
        X: Training set without Class Target
        y:Training set Class Target

    Returns:
        balanced train_x, test_x
    """
    sample = RandomOverSampler(random_state=42)
    X, y = sample.fit_resample(X, y)
    print('after balancing:', X.shape)
    return X, y