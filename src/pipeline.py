import pandas as pd

from Config import Config
from llm_client import LLM, LLMProvider, get_llm_client
from preprocess import load_csv, preprocess_dataframe


def run_pipeline(
    output_path: str, provider: LLM, tickets: pd.DataFrame
) -> pd.DataFrame | None:
    """
    Run the pipeline to classify tickets and save results to a CSV file.
        :param output_path: Path to save the output CSV file.
        :param provider: LLM provider instance.
        :param tickets: DataFrame containing the tickets to classify.
    """

    tickets = preprocess_dataframe(tickets)

    if tickets.empty:
        print("No tickets to process after preprocessing.")
        return

    summaries = []
    categories = []
    confidences = []

    total_tickets = len(tickets)
    print(f"Processing {total_tickets} tickets")

    for idx, row in tickets.iterrows():
        text = row.get("descricao_clean", "") or ""

        summary = provider.summarize(text)
        category, confidence = provider.classify(text, CATEGORIES)

        summaries.append(summary)
        categories.append(category)
        confidences.append(confidence)

        # tracking progress
        processed = idx + 1
        percentage = (processed / total_tickets) * 100
        print(f"Processed {processed}/{total_tickets} rows ({percentage:.2f}%)")

    tickets["summary"] = summaries
    tickets["category"] = categories
    tickets["confidence"] = confidences

    tickets.to_csv(output_path, index=False, sep=";")

    return tickets


if __name__ == "__main__":
    CATEGORIES = [
        "Reclamação",
        "Suporte Técnico",
        "Feedback",
        "Dúvida",
        "Solicitação de Serviço",
    ]
    print(Config)

    provider = Config["PROVIDER"]
    output_path = Config["OUTPUT_CSV"]

    if provider not in LLMProvider._member_names_:
        raise ValueError(f"Unknown LLM provider: {provider}")

    llm_client = get_llm_client(LLMProvider.from_string(provider))
    print(f"Using LLM provider: {provider}")

    print(f"Loading data from {Config['INPUT_CSV']}")
    tickets = load_csv()
    print(f"Loaded {len(tickets)} tickets")

    if tickets.empty:
        print("No tickets to process. Exiting.")
    else:
        print("Running pipeline...")
        run_pipeline(output_path, llm_client, tickets)
        print(f"Results saved to {output_path}")
