import ollama

from config.settings import LLM_MODEL, OLLAMA_HOST


SYSTEM_PROMPT = """You are a financial filings question-answering assistant.

Answer questions using only the provided SEC filing excerpts.

Rules:
1. Use only information contained in the provided context.
2. If the context does not contain enough information to answer, say:
   "I don't have enough information in the retrieved filings to answer that."
3. Do not invent facts, numbers, dates, companies, or transactions.
4. When answering numerical questions, preserve the exact value and units from the source.
5. Keep the answer concise.
"""


class Generator:
    def __init__(self, model_name=LLM_MODEL, host=OLLAMA_HOST):
        self.model_name = model_name
        self.client = ollama.Client(host=host)

    def generate(self, question, contexts):
        if not contexts:
            return "I don't have enough information in the retrieved filings to answer that."

        context_blocks = []

        for rank, context in enumerate(contexts, start=1):
            context_blocks.append(
                f"""SOURCE {rank}
Company: {context["company_name"]}
Filing date: {context["filing_date"]}
Form: {context["form_type"]}
Item: {context["item"]}
Accession: {context["accession_number"]}

{context["text"]}
"""
            )

        context_text = "\n\n".join(context_blocks)

        prompt = f"""Context from SEC filings:

{context_text}

Question:
{question}

Answer using only the context above.
"""

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response["message"]["content"].strip()