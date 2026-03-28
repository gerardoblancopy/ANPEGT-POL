"""Corpus ingestion orchestrator."""

import logging

from anpegt.schema.config import SystemConfig
from anpegt.schema.corpus import CorpusDocument, ChunkRecord
from anpegt.corpus.processors.cleaner import clean_text
from anpegt.corpus.processors.chunker import chunk_text
from anpegt.corpus.processors.classifier import KeywordClassifier
from anpegt.corpus.registry import SourceRegistry

logger = logging.getLogger(__name__)


class CorpusIngester:
    """Orchestrates corpus ingestion: fetch, clean, chunk, classify.

    Parameters
    ----------
    config:
        The system configuration containing corpus sources, clusters,
        and voter segment definitions.
    """

    def __init__(self, config: SystemConfig) -> None:
        self.config = config
        self.registry = SourceRegistry()
        self.classifier = KeywordClassifier(config.clusters)

        # Accumulated results accessible via properties
        self._documents: list[CorpusDocument] = []
        self._chunks: list[ChunkRecord] = []

    @property
    def documents(self) -> list[CorpusDocument]:
        """All ingested documents."""
        return self._documents

    @property
    def chunks(self) -> list[ChunkRecord]:
        """All generated chunks."""
        return self._chunks

    def ingest_source(self, source_id: str) -> int:
        """Ingest documents from a single configured source.

        Parameters
        ----------
        source_id:
            The ID of the corpus source (as defined in config).

        Returns
        -------
        int
            Number of documents ingested.
        """
        # Find the source definition
        source_def = None
        for s in self.config.corpus_sources:
            if s.id == source_id:
                source_def = s
                break

        if source_def is None:
            logger.warning("Source %s not found in configuration", source_id)
            return 0

        if not source_def.enabled:
            logger.info("Source %s is disabled, skipping", source_id)
            return 0

        # Get the source implementation
        try:
            source = self.registry.get_source(source_def.source_type)
        except KeyError as exc:
            logger.warning("Cannot ingest source %s: %s", source_id, exc)
            return 0

        # Fetch raw documents
        raw_config = {
            "id": source_def.id,
            "path_or_url": source_def.path_or_url,
            **source_def.metadata,
        }
        raw_docs = source.fetch(raw_config)

        # Process each document
        count = 0
        for doc in raw_docs:
            # Clean
            doc.cleaned_text = clean_text(doc.raw_text)

            # Classify into clusters
            doc.cluster_tags = self.classifier.classify(doc.cleaned_text)

            # Classify into voter segments
            doc.segment_tags = self.classifier.classify_segment(
                doc.cleaned_text, self.config.voter_segments
            )

            self._documents.append(doc)

            # Chunk
            text_chunks = chunk_text(doc.cleaned_text)
            for idx, chunk_text_str in enumerate(text_chunks):
                chunk = ChunkRecord(
                    document_id=doc.source_id,
                    chunk_index=idx,
                    text=chunk_text_str,
                    cluster_tags=doc.cluster_tags,
                    segment_tags=doc.segment_tags,
                )
                self._chunks.append(chunk)

            count += 1

        logger.info(
            "Ingested %d documents (%d chunks) from source %s",
            count,
            len(text_chunks) if raw_docs else 0,
            source_id,
        )
        return count

    def ingest_all(self) -> int:
        """Ingest documents from all enabled corpus sources.

        Returns
        -------
        int
            Total number of documents ingested.
        """
        total = 0
        for source_def in self.config.corpus_sources:
            if source_def.enabled:
                total += self.ingest_source(source_def.id)

        logger.info(
            "Total ingestion: %d documents, %d chunks",
            len(self._documents),
            len(self._chunks),
        )
        return total
