import asyncio

from app.documents.pdf import PDFParser


async def main():
    document = await PDFParser().parse("test_document.pdf")

    print("filename:", document.filename)
    print("type:", document.document_type)
    print("pages:", len(document.pages))
    print("text:", document.full_text)
    print("metadata:", document.pages[0].metadata)


asyncio.run(main())
