"""Media monitor corpus source."""

import json
import logging
from pathlib import Path

from anpegt.schema.corpus import CorpusDocument
from anpegt.corpus.sources.local_files import _parse_yaml_frontmatter

logger = logging.getLogger(__name__)


class MediaMonitorSource:
    """Reads media monitoring data from .txt and .json files."""

    source_type: str = "media_monitor"

    def fetch(self, config: dict) -> list[CorpusDocument]:
        """Fetch media monitoring documents from text and JSON files.

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
                "MediaMonitorSource: path %s is not a directory", path
            )
            return []

        source_id_prefix = config.get("id", "media_monitor")
        documents: list[CorpusDocument] = []

        for filepath in sorted(path.iterdir()):
            if filepath.suffix == ".txt":
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
                        "MediaMonitorSource: error reading %s: %s",
                        filepath,
                        exc,
                    )
            elif filepath.suffix == ".json":
                try:
                    data = json.loads(filepath.read_text(encoding="utf-8"))
                    text = data.get("text", json.dumps(data))
                    meta = data.get("metadata", {})
                    meta["filename"] = filepath.name
                    documents.append(
                        CorpusDocument(
                            source_type=self.source_type,
                            source_id=f"{source_id_prefix}/{filepath.name}",
                            raw_text=text,
                            metadata=meta,
                        )
                    )
                except (json.JSONDecodeError, KeyError) as exc:
                    logger.warning(
                        "MediaMonitorSource: error reading %s: %s",
                        filepath,
                        exc,
                    )

        logger.info(
            "MediaMonitorSource: fetched %d documents from %s",
            len(documents),
            path,
        )
        return documents
