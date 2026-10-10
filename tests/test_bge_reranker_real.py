import asyncio

from app.rag.reranking.bge import BGEReranker


def test_real_reranker_ranks_relevant_document_higher() -> None:
    reranker = BGEReranker(device="cpu")

    query = "What technical documents must the supplier provide?"

    documents = [
        {
            "id": "irrelevant",
            "payload": {
                "text": "The supplier must deliver all goods to the warehouse by Friday."
            },
        },
        {
            "id": "relevant",
            "payload": {
                "text": (
                    "The supplier must provide technical documentation, "
                    "product specifications, operating manuals, and maintenance guides."
                )
            },
        },
    ]

    results = asyncio.run(
        reranker.rerank(query, documents, top_k=2)
    )

    assert len(results) == 2
    assert results[0]["id"] == "relevant"
    assert results[0]["rerank_score"] > results[1]["rerank_score"]
