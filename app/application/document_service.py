from app.documents.factory import DocumentFactory
from app.domain.models.document import NormalizedDocument


class DocumentService:

    async def parse_document(
        self,
        file_path: str,
    ) -> NormalizedDocument:
        parser = DocumentFactory.create(file_path)

        return await parser.parse(file_path)
