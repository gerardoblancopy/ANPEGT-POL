"""Local files corpus source."""

import json
import logging
from pathlib import Path
from uuid import uuid4

from anpegt.schema.corpus import CorpusDocument

logger = logging.getLogger(__name__)


def _parse_yaml_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from text if present.

    Frontmatter is delimited by --- markers at the start of the file.

    Returns
    -------
    tuple[dict, str]
        (metadata dict, remaining text body)
    """
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    try:
        import yaml

        metadata = yaml.safe_load(parts[1])
        if not isinstance(metadata, dict):
            return {}, text
        body = parts[2].strip()
        return metadata, body
    except Exception:
        return {}, text


class LocalFilesSource:
    """Reads .txt and .json files from a local directory."""

    source_type: str = "local_files"

    def fetch(self, config: dict) -> list[CorpusDocument]:
        """Fetch documents from local files.

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
            logger.warning("LocalFilesSource: path %s is not a directory", path)
            return []

        documents: list[CorpusDocument] = []
        source_id_prefix = config.get("id", "local_files")

        for filepath in sorted(path.iterdir()):
            if filepath.suffix == ".txt":
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
            elif filepath.suffix == ".json":
                try:
                    data = json.loads(filepath.read_text(encoding="utf-8"))
                    text = data.get("text", "")
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
                        "LocalFilesSource: error reading %s: %s",
                        filepath,
                        exc,
                    )

        logger.info(
            "LocalFilesSource: fetched %d documents from %s",
            len(documents),
            path,
        )
        return documents
