from fastapi import FastAPI
from pydantic import BaseModel

from api.retrieval import Retriever
from api.generate import Generator


app = FastAPI(
    title="FilingsQA",
    description="RAG-based SEC filings question-answering system",
    version="0.1.0",
)

retriever = Retriever()
generator = Generator()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search")
def search(request: SearchRequest):
    results = retriever.search(
        request.query,
        top_k=request.top_k,
    )

    return {
        "query": request.query,
        "results": results,
    }


@app.post("/ask")
def ask(request: AskRequest):
    results = retriever.search(
        request.question,
        top_k=request.top_k,
    )

    answer = generator.generate(
        request.question,
        results,
    )

    sources = [
        {
            "company_name": result["company_name"],
            "filing_date": result["filing_date"],
            "item": result["item"],
            "accession_number": result["accession_number"],
            "score": result["score"],
        }
        for result in results
    ]

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }