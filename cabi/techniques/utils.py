from sklearn import metrics


def simple_classification(
        model, Xtrain, ytrain, Xtest=None, ytest=None):
    model.fit(Xtrain, ytrain)

    if Xtest is not None:
        prob = model.predict_proba(Xtest)

        classified = []
        for p in prob:
            classified.append(1 if p[1] >= 0.5 else 0)

        print(
            "Brier Score loss:",
            metrics.brier_score_loss(ytest, [p[1] for p in prob]),
            "\nClassification Report:\n",
            metrics.classification_report(ytest, classified))

    return model
