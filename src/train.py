import pandas as pd
import mlflow
import mlflow.sklearn
import dagshub
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix
)

dagshub.init(repo_owner='eyacherif03', repo_name='mlops-water-potability-1', mlflow=True)
mlflow.set_tracking_uri("https://dagshub.com/eyacherif03/mlops-water-potability-1.mlflow")
EXPERIMENT_NAME = "Experiment1"
mlflow.set_experiment(EXPERIMENT_NAME)


def train():
    train_data = pd.read_csv("/app/dataset/processed/train.csv")
    test_data  = pd.read_csv("/app/dataset/processed/test.csv")

    X_train = train_data.drop(columns=["Potability"])
    y_train = train_data["Potability"]
    X_test  = test_data.drop(columns=["Potability"])
    y_test  = test_data["Potability"]

    n_estimators = 300

    os.makedirs("/app/reports", exist_ok=True)

    with mlflow.start_run(run_name="random_forest"):
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            class_weight='balanced',
            random_state=0
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Métriques
        acc       = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall    = recall_score(y_test, y_pred)
        f1        = f1_score(y_test, y_pred)

        # Log MLflow
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("class_weight", "balanced")
        mlflow.log_param("model_name",   "RandomForest")
        mlflow.log_metric("accuracy",    acc)
        mlflow.log_metric("precision",   precision)
        mlflow.log_metric("recall",      recall)
        mlflow.log_metric("f1_score",    f1)
        mlflow.set_tag("model",  "RandomForest")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(5, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title("Confusion Matrix — RandomForest")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.savefig("/app/reports/cm_random_forest.png")
        plt.close()
        mlflow.log_artifact("/app/reports/cm_random_forest.png")

        # Sauvegarde modèle
        model_dir = "/tmp/rf_model"
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)
        mlflow.sklearn.save_model(model, model_dir)
        mlflow.log_artifacts(model_dir, artifact_path="model")

        print(f"Accuracy  : {acc:.4f}")
        print(f"Precision : {precision:.4f}")
        print(f"Recall    : {recall:.4f}")
        print(f"F1-score  : {f1:.4f}")

    print("Training done")


if __name__ == "__main__":
    train()