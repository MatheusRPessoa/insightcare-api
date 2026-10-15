from pathlib import Path

import pandas as pd
from datasets import load_dataset

DATASET_NAME = (
    "RichardSakaguchiMS/"
    "brazilian-customer-service-conversations"
)

OUTPUT_DIR = Path("ml/data")


def prepare_split(dataset) -> pd.DataFrame:
    rows = []

    for example in dataset:
        messages = example["messages"]
        metadata = example["metadata"]

        customer_messages = [
            message["content"]
            for message in messages
            if message["role"] == "customer"
        ]

        text = " ".join(customer_messages).strip()

        if not text:
            continue

        rows.append(
            {
                "id": example["id"],
                "text": text,
                "intent": metadata["intent"],
                "sentiment": metadata["sentiment"],
                "sector": metadata["sector"], 
            }
        )
    
    return pd.DataFrame(rows)


def main() -> None:
    dataset = load_dataset(DATASET_NAME)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for split_name in ("train", "validation", "test"):
        dataframe = prepare_split(dataset[split_name])

        output_path = OUTPUT_DIR / f"{split_name}.csv"

        dataframe.to_csv(
            output_path,
            index=False,
            encoding="utf-8",
        )

        print(f"\n{split_name.upper()}")
        print(f"Registros: {len(dataframe)}")
        print("Intenções:")
        print(dataframe["intent"].value_counts())
        print(f"Arquivo: {output_path}")


if __name__ == "__main__":
    main()