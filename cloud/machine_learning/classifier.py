from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis, LinearDiscriminantAnalysis
import sklearn.model_selection as model_selection
import sklearn.svm as svm


def best_classifier(X, y, n_folds, metric):
    """Generates candidates for QuadraticDiscriminantAnalysis from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'reg_param': [0.001],
        'store_covariance': [True],
        'tol': [5e-05]  # , 0.01, 0.1
    }

    clf = model_selection.GridSearchCV(QuadraticDiscriminantAnalysis(), param_grid, scoring=metric, cv=n_folds,
                                       refit=True,
                                       n_jobs=-1)
    clf.fit(X, y)
    return clf


def svm_param_selection(X, y, n_folds, metric):
    """Generates candidates for svm.SVC from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    """param_grid = [{'kernel': ['rbf'], 'gamma': ['auto', 'scale'], 'C': [0.1, 1, 10]},
                  {'kernel': ['linear'], 'C': [0.1, 1, 10]},
                  {'kernel': ['poly'], 'gamma': ['scale'], 'C': [0.1, 1, 10], 'degree':[2, 3]},
                  {'kernel': ['sigmoid'], 'gamma': ['scale'], 'C': [0.1, 1, 10]}]"""
    param_grid = {
        'kernel': ['poly'],
        'C': [400],
        'gamma': ['scale'],
        'degree': [2],
    }

    clf = model_selection.GridSearchCV(svm.SVC(), param_grid, scoring=metric, cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)

    return clf


def gpc_param_selection(X, y, n_folds, metric):
    """Generates candidates for GaussianProcessClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    # WARNING, RAM SATURATION
    parameters = [{
        'kernel': [1.0 * RBF(1.0)],
        'warm_start': [True],
        'random_state': [42],
        'max_iter_predict': [1000],
        'n_restarts_optimizer': [0],
        'copy_X_train': [False]
    }]

    clf = model_selection.GridSearchCV(GaussianProcessClassifier(), param_grid=parameters, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def mlp_param_selection(X, y, n_folds, metric):
    """Generates candidates for MLPClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    parameters = [{
        'hidden_layer_sizes': [(100, 50)],
        'activation': ['relu'],
        'solver': ['sgd'],
        'learning_rate_init': [.01],
        'learning_rate': ['adaptive'],
        'max_iter': [1000]
    }]

    clf = model_selection.GridSearchCV(MLPClassifier(), param_grid=parameters, scoring=metric, cv=n_folds,
                                       refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def mlp_param_selection_first_paramgrid(X, y, n_folds, metric):
    """Generates candidates for MLPClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    parameters = {
        'hidden_layer_sizes': (10, 120, 10),
        'activation': ('identity', 'logistic', 'tanh', 'relu'),
        'alpha': (0.000001, 0.00001, 0.0001),
        'solver': ('lbfgs', 'sgd', 'adam'),
    }
    clf = model_selection.GridSearchCV(MLPClassifier(batch_size='auto', warm_start=True, max_iter=2000),
                                       param_grid=parameters, scoring=metric, cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def mlp_param_selection_second_paramgrid(X, y, n_folds, metric):
    """Generates candidates for MLPClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    parameters = {
        'hidden_layer_sizes': (10,120,10),
        'activation': ('identity', 'logistic', 'tanh', 'relu'),
        'alpha': (0.000001, 0.00001, 0.0001),
        'learning_rate': ('constant', 'invscaling', 'adaptive'),
        'momentum': (0.1,0.9,0.1),
    }
    clf = model_selection.GridSearchCV(MLPClassifier(batch_size='auto', warm_start=True, solver='sgd',
                                                     max_iter=1000, early_stopping=True), param_grid=parameters,
                                       scoring=metric, cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def mlp_param_selection_third_paramgrid(X, y, n_folds, metric):
    """Generates candidates for MLPClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    parameters = {
        'hidden_layer_sizes': (10, 120, 10),
        'activation': ('identity', 'logistic', 'tanh', 'relu'),
        'alpha': (0.000001, 0.00001, 0.0001),
        'beta_1': (0.1, 0.9, 0.1),
        'beta_2': (0.1, 0.9, 0.1),
    }
    clf = model_selection.GridSearchCV(MLPClassifier(batch_size='auto', warm_start=True, solver='adam', max_iter=400,
                                                     early_stopping=True), param_grid=parameters, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def random_forest_param_selection(X, y, n_folds, metric):
    """Generates candidates for RandomForestClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'min_samples_leaf': [1],
        'n_estimators': [1000],
        'n_jobs': [-1],
        'class_weight': ["balanced"],
        'criterion': ["entropy"],
        'max_depth': [15],
        'min_samples_split': [3]
    }

    clf = model_selection.GridSearchCV(RandomForestClassifier(), param_grid, scoring=metric, cv=n_folds, refit=True,
                                       n_jobs=-1)
    clf.fit(X, y)
    return clf


def qda_param_selection(X, y, n_folds, metric):
    """Generates candidates for QuadraticDiscriminantAnalysis from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'reg_param': (0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.05, 0.1),
        'store_covariance': (True, False),
        'tol': (0.0000005, 0.000005, 0.00005)
    }

    clf = model_selection.GridSearchCV(QuadraticDiscriminantAnalysis(), param_grid, scoring=metric, cv=n_folds,
                                       refit=True,
                                       n_jobs=-1)
    clf.fit(X, y)
    return clf


def lda_shrink_param_selection(X, y, n_folds, metric):
    """Generates candidates for LinearDiscriminantAnalysis from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'solver': ('lsqr', 'eigen'),
        'n_components': (1, 5, 1),
    }

    clf = model_selection.GridSearchCV(LinearDiscriminantAnalysis(shrinkage='auto'), param_grid, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def lda_svd_param_selection(X, y, n_folds, metric):
    """Generates candidates for LinearDiscriminantAnalysis from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'store_covariance': (True, False),
        'n_components': (0, 5, 1),
    }

    clf = model_selection.GridSearchCV(LinearDiscriminantAnalysis(solver='svd', ), param_grid, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def gnb_param_selection(X, y, n_folds, metric):
    """Generates candidates for GaussianNB from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'var_smoothing': (0, 1e-9, 1e-7, 1e-5)
    }

    clf = model_selection.GridSearchCV(GaussianNB(), param_grid, scoring=metric, cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def decision_tree_bagging_param_selection(X, y, n_folds, metric):
    """Generates candidates for BaggingClassifier(DecisionTreeClassifier()) from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'base_classifier__min_samples_leaf': [1],
        'n_estimators': [100],
        'n_jobs': [-1],
        'base_classifier__class_weight': ["balanced"],
        'base_classifier__criterion': ["gini"],
        'base_classifier__max_depth': [70, 80],
        'base_classifier__min_samples_split': [3, 4],
        'base_classifier__max_features': ['auto'],
        'base_classifier__random_state': [42],
        'warm_start': [True],
        'bootstrap_features': [True]
    }
    clf = model_selection.GridSearchCV(BaggingClassifier(DecisionTreeClassifier()), param_grid, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def k_neighbors_param_selection(X, y, n_folds, metric):
    """Generates candidates for KNeighborsClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'n_neighbors': (1, 10, 1),
        'leaf_size': (20, 40, 1),
        'p': (1, 2),
        'weights': ('uniform', 'distance'),
        'metric': ('minkowski', 'chebyshev'),
    }

    clf = model_selection.GridSearchCV(KNeighborsClassifier(), param_grid, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def perceptron_adaboost_param_selection(X, y, n_folds, metric):
    """Generates candidates for AdaBoostClassifier(Perceptron()) from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = [{
    }]
    clf = model_selection.GridSearchCV(AdaBoostClassifier(Perceptron(), algorithm='SAMME'), param_grid, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def gbc_param_selection(X, y, n_folds, metric):
    """Generates candidates for GradientBoostingClassifier from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'learning_rate':[0.15,0.1,0.05,0.01,0.005,0.001],
        'n_estimators':[100,250,500,750,1000,1250,1500,1750]
    }

    clf = model_selection.GridSearchCV(GradientBoostingClassifier(max_depth=4, min_samples_split=2, min_samples_leaf=1, subsample=1,max_features='sqrt', random_state=10), param_grid, scoring=metric,
                                       cv=n_folds, refit=True, n_jobs=-1)
    clf.fit(X, y)
    return clf


def nuSvm_param_selection(X, y, n_folds, metric):
    """Generates candidates for svm.NuSVC from a grid of parameter

    Args:
        X: Training set without Class Target
        y: Training set Class Target
        n_folds: Number of cross validation fold
        metric: metric on which to base your results

    Returns: classifiers' configurations

    """
    param_grid = {
        'class_weight': ["balanced"],
        'kernel': ['poly', 'rbf'],
        'gamma': ['scale', 'auto'],
        'degree': [2],
        'coef0': [0, 0.3]
    }

    clf = model_selection.GridSearchCV(svm.NuSVC(nu=0.26), param_grid, scoring=metric, cv=n_folds, refit=True,
                                       n_jobs=-1)
    clf.fit(X, y)
    return clf