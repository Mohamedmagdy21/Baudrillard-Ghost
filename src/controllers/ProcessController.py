from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.models import ProcessingEnums
from src.models.db_schema.chunk_metadata import ChunkMetaData
from src.stores.llm.LLMEnums import DocumentTypeEnum
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Element
from nltk.tokenize import sent_tokenize
import numpy as np
import asyncio
import nltk
nltk.download('punkt_tab', quiet=True)

class ProcessController(BaseController):

    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self,file_id:str):
        return os.path.splitext(file_id)[-1]

    async def get_file_content(self, file_id: str):
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(self.project_path, file_id)

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnums.PDF.value:
            return await asyncio.to_thread(partition_pdf, file_path)

        if file_ext == ProcessingEnums.TXT.value:
            loader = TextLoader(file_path, encoding="utf-8")
            return await asyncio.to_thread(loader.load)

        return None

    def _segregate_chapters(self, elements, book_name):
        current_chapter = "Unknown"
        chapter_text = []
        chapter_pages = []
        chapters = []

        for el in elements:
            cat = el.category if hasattr(el, 'category') else ""

            if cat == "Title":
                if chapter_text:
                    chapters.append({
                        "chapter": current_chapter,
                        "text": "\n\n".join(chapter_text),
                        "pages": chapter_pages
                    })
                    chapter_text = []
                    chapter_pages = []
                current_chapter = el.text.strip() or current_chapter
                continue

            if cat in ("NarrativeText", "Paragraph", "ListItem", "UncategorizedText"):
                text = el.text.strip()
                if not text:
                    continue
                chapter_text.append(text)
                chapter_pages.append(el.metadata.page_number if el.metadata else None)

        if chapter_text:
            chapters.append({
                "chapter": current_chapter,
                "text": "\n\n".join(chapter_text),
                "pages": chapter_pages
            })

        return chapters

    def _make_chunk(self, text, chapter_name, book_name, chapter_pages, chunk_order):
        min_p = min(chapter_pages) if chapter_pages else 0
        max_p = max(chapter_pages) if chapter_pages else 0
        return {
            "chunk_text": text,
            "chunk_metadata": ChunkMetaData(
                book_name=book_name,
                chapter=chapter_name,
                page=min_p,
                page_range=f"{min_p}-{max_p}" if min_p != max_p else str(min_p)
            ),
            "chunk_order": chunk_order,
        }

    def _semantic_chunk_chapters(self, chapters, embedding_client, book_name, max_chunk_size=2000, similarity_threshold=0.5):
        all_chunks = []
        chunk_order = 0

        for chapter in chapters:
            chapter_name = chapter["chapter"]
            chapter_text = chapter["text"]
            chapter_pages = [p for p in chapter["pages"] if p is not None]

            sentences = sent_tokenize(chapter_text)
            if len(sentences) <= 1:
                chunk_order += 1
                all_chunks.append(self._make_chunk(chapter_text, chapter_name, book_name, chapter_pages, chunk_order))
                continue

            embeddings = embedding_client.embed_text_batch(
                texts=sentences,
                document_type=DocumentTypeEnum.DOCUMENT.value
            )

            similarities = []
            for i in range(len(embeddings) - 1):
                a = np.array(embeddings[i])
                b = np.array(embeddings[i + 1])
                sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
                similarities.append(sim)

            split_indices = [0]
            for i, sim in enumerate(similarities):
                if sim < similarity_threshold:
                    split_indices.append(i + 1)
            split_indices.append(len(sentences))

            for i in range(len(split_indices) - 1):
                start = split_indices[i]
                end = split_indices[i + 1]
                chunk_sents = sentences[start:end]
                chunk_text = " ".join(chunk_sents)

                if len(chunk_text.strip()) < 10:
                    continue

                if len(chunk_text) > max_chunk_size:
                    current = ""
                    for sent in chunk_sents:
                        if len(current) + len(sent) > max_chunk_size and current:
                            chunk_order += 1
                            all_chunks.append(self._make_chunk(current.strip(), chapter_name, book_name, chapter_pages, chunk_order))
                            current = sent
                        else:
                            current = (current + " " + sent).strip()
                    if current:
                        chunk_order += 1
                        all_chunks.append(self._make_chunk(current.strip(), chapter_name, book_name, chapter_pages, chunk_order))
                else:
                    chunk_order += 1
                    all_chunks.append(self._make_chunk(chunk_text, chapter_name, book_name, chapter_pages, chunk_order))

        return all_chunks

    async def process_file_content(self, file_content, file_id, embedding_client=None, max_chunk_size=2000):
        if not file_content:
            return None

        book_name = os.path.splitext(file_id)[0]

        if isinstance(file_content[0], Element):
            chapters = self._segregate_chapters(file_content, book_name)
            if not chapters:
                return None
            return self._semantic_chunk_chapters(chapters, embedding_client, book_name, max_chunk_size)

        splitter = RecursiveCharacterTextSplitter(chunk_size=max_chunk_size, chunk_overlap=0, length_function=len)
        docs = splitter.create_documents([rec.page_content for rec in file_content])
        return [
            {
                "chunk_text": doc.page_content,
                "chunk_metadata": ChunkMetaData(
                    book_name=book_name,
                    chapter="Unknown",
                    page=0,
                    page_range="0"
                ),
                "chunk_order": i + 1,
            }
            for i, doc in enumerate(docs)
        ]
