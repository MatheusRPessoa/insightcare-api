from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline

DATA_DIR = Path(__file__).resolve().parent / "data"
MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "intent_classifier.joblib"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA_DIR / "train.csv")
    validation = pd.read_csv(DATA_DIR / "validation.csv")
    test = pd.read_csv(DATA_DIR / "test.csv")

    return train, validation, test


def create_model(c: float = 1.0) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=c,
                    max_iter=2000,
                    random_state=42,
                ),
            ),  
        ]
    )


def evaluate(model: Pipeline, data: pd.DataFrame) -> dict:
    predictions = model.predict(data["text"])

    return {
        "accuracy": accuracy_score(
            data["intent"], predictions
        ),
        "f1_macro": f1_score(
            data["intent"],
            predictions,
            average="macro",
            zero_division=0,
        ),
        "report": classification_report(
            data["intent"],
            predictions,
            zero_division=0,
        ),
        "predictions": predictions,
    }


def train() -> None:
    train_df, validation_df, test_df = load_data()


    print("Treino:", len(train_df))
    print("Validação:", len(validation_df))
    print("Teste:", len(test_df))

    best_model = None
    best_score = -1.0
    best_c = None

    for c in (0.1, 1.0, 10.0):
        model = create_model(c)

        model.fit(
            train_df["text"],
            train_df["intent"],
        )

        result = evaluate(model, validation_df)

        score = result["f1_macro"]

        print(
            f"C={c} | "
            f"Accuracy={result['accuracy']:.4f} | "
            f"F1 macro={score:.4f}"
        )

        if score > best_score:
            best_score = score
            best_model = model
            best_c = c

    
    assert best_model is not None

    print(f"\nMelhor C: {best_c}")


    final_train = pd.concat(
        [train_df, validation_df],
        ignore_index=True,
    )

    final_model = create_model(best_c)

    final_model.fit(
        final_train["text"],
        final_train["intent"],
    )

    test_result = evaluate(final_model, test_df)
        
    print("\n=== AVALIAÇÃO NO TESTE ===")
    print(f"Accuracy: {test_result['accuracy']:.4f}")
    print(test_result["report"])

    print("Matriz de confusão:")
    print(
        confusion_matrix(
            test_df["intent"],
            test_result["predictions"],
            labels=final_model.classes_,
        )
    )
    print("Ordem das classes:", final_model.classes_)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(final_model, MODEL_PATH)

    print(f"\nModelo salvo em: {MODEL_PATH}")


if __name__ == "__main__":
    train()
