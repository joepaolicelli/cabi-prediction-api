from cabi.techniques.utils import simple_classification
from sklearn import linear_model


def logistic_regression(Xtr, ytr, Xte=None, yte=None):
    simple_classification(
        linear_model.LogisticRegression(), Xtr, ytr, Xte, yte)


def logistic_regression_cv(Xtr, ytr, Xte=None, yte=None):
    simple_classification(
        linear_model.LogisticRegressionCV(), Xtr, ytr, Xte, yte)


def log_sgd(Xtr, ytr, Xte=None, yte=None):
    simple_classification(
        linear_model.SGDClassifier(loss="log"), Xtr, ytr, Xte, yte)
