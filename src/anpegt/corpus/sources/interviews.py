"""Interviews corpus source."""

import logging
from pathlib import Path

from anpegt.schema.corpus import CorpusDocument
from anpegt.corpus.sources.local_files import _parse_yaml_frontmatter

logger = logging.getLogger(__name__)


class InterviewsSource:
    """Reads interview transcriptions from .txt files."""

    source_type: str = "interviews"

    def fetch(self, config: dict) -> list[CorpusDocument]:
        """Fetch interview documents from text files.

        Parameters
        ----------
        config:
            Must contain 'path_or_url' pointing to a directory.

        Returns
        -------
        list[CorpusDocument]
            Ingested documents.
        """
        path = Path(config.get("path_or_url", ""))
        if not path.is_dir():
            logger.warning(
                "InterviewsSource: path %s is not a directory", path
            )
            return []

        source_id_prefix = config.get("id", "interviews")
        documents: list[CorpusDocument] = []

        for filepath in sorted(path.glob("*.txt")):
            try:
                raw = filepath.read_text(encoding="utf-8")
                metadata, body = _parse_yaml_frontmatter(raw)
                metadata["filename"] = filepath.name
                documents.append(
                    CorpusDocument(
                        source_type=self.source_type,
                        source_id=f"{source_id_prefix}/{filepath.name}",
                        raw_text=body,
                        metadata=metadata,
                    )
                )
            except Exception as exc:
                logger.warning(
                    "InterviewsSource: error reading %s: %s", filepath, exc
                )

        logger.info(
            "InterviewsSource: fetched %d documents from %s",
            len(documents),
            path,
        )
        return documents
