from cabi.techniques.utils import simple_classification
from sklearn import ensemble
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline


def brbm_rf(Xtr, ytr, Xte=None, yte=None):
    randomforest = ensemble.RandomForestClassifier(n_jobs=-1, n_estimators=100)
    rbm = BernoulliRBM(random_state=0)
    classifier = Pipeline(steps=[('rbm', rbm), ('randomforest', randomforest)])

    rbm.learning_rate = 0.025
    rbm.n_iter = 250
    rbm.n_components = 100

    return simple_classification(
        classifier, Xtr, ytr, Xte, yte)
