import torch
import faiss
import edgar
import fastapi
import sentence_transformers


def test_pytorch_available():
    assert torch.__version__


def test_faiss_available():
    assert faiss.__version__


def test_edgartools_available():
    assert edgar


def test_fastapi_available():
    assert fastapi


def test_sentence_transformers_available():
    assert sentence_transformers