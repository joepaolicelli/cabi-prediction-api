from cabi.techniques.utils import simple_classification
from sklearn import ensemble


def random_forest(Xtr, ytr, Xte, yte):
    simple_classification(
        ensemble.RandomForestClassifier(n_jobs=-1, n_estimators=100),
        Xtr, ytr, Xte, yte)


def ada_boost(Xtr, ytr, Xte, yte):
    simple_classification(
        ensemble.AdaBoostClassifier(), Xtr, ytr, Xte, yte)


def bagging(Xtr, ytr, Xte, yte):
    simple_classification(
        ensemble.BaggingClassifier(), Xtr, ytr, Xte, yte)
