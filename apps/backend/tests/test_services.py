"""Unit tests for service-layer pieces that previously had silent bugs."""

import pytest
from langchain_core.documents import Document

from app.services.langchain_service import normalize_advanced_config, DEFAULT_ADVANCED_CONFIG
from app.services.pinecone_service import PineconeService, PineconeNotConfiguredError
from app.services.aws_service import AWS_Service, S3NotConfiguredError
from app.utils.preprocessing import TextSplitter
from app.utils.password import get_password_hash, verify_password


def test_password_hash_roundtrip():
    hashed = get_password_hash("hunter2!")
    assert hashed != "hunter2!"
    assert verify_password("hunter2!", hashed)
    assert not verify_password("wrong", hashed)


def test_normalize_advanced_config_none():
    config = normalize_advanced_config(None)
    assert config == DEFAULT_ADVANCED_CONFIG


def test_normalize_advanced_config_snake_case_dict():
    config = normalize_advanced_config({"chunk_size": 256, "llm_model": "gpt-4o"})
    assert config["chunkSize"] == 256
    assert config["llmModel"] == "gpt-4o"
    # defaults are preserved for everything else
    assert config["pdfParser"] == "PyPDFParser"


def test_normalize_advanced_config_camel_case_dict():
    config = normalize_advanced_config({"chunkSize": 128})
    assert config["chunkSize"] == 128


def test_text_splitter_returns_documents_with_string_content():
    splitter = TextSplitter("recursive", chunk_size=50, chunk_overlap=0)
    docs = splitter.split_texts([Document(page_content="word " * 100)])
    assert len(docs) > 1
    for doc in docs:
        assert isinstance(doc.page_content, str)


def test_text_splitter_accepts_ui_strategy_name():
    splitter = TextSplitter("RecursiveCharacterTextSplitter", chunk_size=50, chunk_overlap=0)
    chunks = splitter.split_text("word " * 100)
    assert all(isinstance(c, str) for c in chunks)


def test_pinecone_unconfigured_raises_clear_error(monkeypatch):
    service = PineconeService()
    from app.services import pinecone_service as ps
    monkeypatch.setattr(ps.settings, "PINECONE_API_KEY", "")
    assert not service.is_configured
    with pytest.raises(PineconeNotConfiguredError):
        _ = service.client


def test_s3_unconfigured_raises_clear_error(monkeypatch):
    service = AWS_Service()
    from app.services import aws_service as awss
    monkeypatch.setattr(awss.settings, "AWS_ACCESS_KEY_ID", "")
    assert not service.is_configured
    with pytest.raises(S3NotConfiguredError):
        _ = service.s3_client


def test_rrf_fusion_ordering():
    from app.services.langchain_service import LangChainService

    class FakeMatch:
        def __init__(self, id):
            self.id = id

    service = LangChainService()
    a, b, c = FakeMatch("a"), FakeMatch("b"), FakeMatch("c")
    fused = service.reciprocal_rank_fusion([[a, b], [b, c], [b, a]])
    # 'b' appears most highly ranked overall
    assert fused[0].id == "b"
