from app.application.container import ApplicationContainer
from app.llm.provider import OllamaLLMProvider


def make_container(monkeypatch, *, llm_provider=None):
    monkeypatch.setattr(
        "app.application.rag_factory.create_retrieval_service",
        lambda: "fake-retriever",
    )

    kwargs = {
        "research_provider": object(),
        "security_scanner": object(),
    }

    if llm_provider is not None:
        kwargs["llm_provider"] = llm_provider

    return ApplicationContainer.with_rag(**kwargs)


def test_container_creates_local_ollama_provider(monkeypatch):
    monkeypatch.setattr("app.application.container.settings.llm_provider", "ollama")
    monkeypatch.setattr("app.application.container.settings.llm_model", "qwen2.5:7b")
    monkeypatch.setattr(
        "app.application.container.settings.ollama_base_url",
        "http://localhost:11434",
    )
    container = make_container(monkeypatch)

    assert isinstance(container.llm_provider, OllamaLLMProvider)
    assert container.llm_provider.model == "qwen2.5:7b"
    assert container.llm_provider.base_url == "http://localhost:11434"
    assert container.retriever == "fake-retriever"


def test_container_preserves_injected_provider(monkeypatch):
    custom_provider = object()

    container = make_container(
        monkeypatch,
        llm_provider=custom_provider,
    )

    assert container.llm_provider is custom_provider


def test_container_exposes_tender_ingestion_service(monkeypatch):
    from app.application.tender_ingestion_service import TenderIngestionService

    fake_ingestion_service = object()

    monkeypatch.setattr(
        "app.application.rag_factory.create_retrieval_service",
        lambda: "fake-retriever",
    )
    monkeypatch.setattr(
        "app.application.rag_factory.create_tender_ingestion_service",
        lambda: fake_ingestion_service,
    )
    monkeypatch.setattr(
        "app.application.container.settings.llm_provider",
        "ollama",
    )

    container = ApplicationContainer.with_rag(
        research_provider=object(),
        llm_provider=object(),
        security_scanner=object(),
    )

    assert container.create_tender_ingestion_service() is fake_ingestion_service
