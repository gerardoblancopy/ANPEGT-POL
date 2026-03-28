"""Surveys corpus source."""

import csv
import json
import logging
from pathlib import Path

from anpegt.schema.corpus import CorpusDocument

logger = logging.getLogger(__name__)


class SurveysSource:
    """Reads survey data from CSV and JSON files."""

    source_type: str = "surveys"

    def fetch(self, config: dict) -> list[CorpusDocument]:
        """Fetch survey documents from CSV/JSON files.

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
                "SurveysSource: path %s is not a directory", path
            )
            return []

        source_id_prefix = config.get("id", "surveys")
        documents: list[CorpusDocument] = []

        # Read JSON files
        for filepath in sorted(path.glob("*.json")):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for idx, item in enumerate(data):
                        text = item.get("text", json.dumps(item))
                        meta = item.get("metadata", {})
                        meta["filename"] = filepath.name
                        documents.append(
                            CorpusDocument(
                                source_type=self.source_type,
                                source_id=f"{source_id_prefix}/{filepath.stem}_{idx}",
                                raw_text=text,
                                metadata=meta,
                            )
                        )
                elif isinstance(data, dict):
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
                    "SurveysSource: error reading %s: %s", filepath, exc
                )

        # Read CSV files
        for filepath in sorted(path.glob("*.csv")):
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    reader = csv.DictReader(fh)
                    for idx, row in enumerate(reader):
                        text = row.get("text", row.get("response", str(row)))
                        metadata = dict(row)
                        metadata["filename"] = filepath.name
                        documents.append(
                            CorpusDocument(
                                source_type=self.source_type,
                                source_id=f"{source_id_prefix}/{filepath.stem}_{idx}",
                                raw_text=text,
                                metadata=metadata,
                            )
                        )
            except Exception as exc:
                logger.warning(
                    "SurveysSource: error reading %s: %s", filepath, exc
                )

        logger.info(
            "SurveysSource: fetched %d documents from %s",
            len(documents),
            path,
        )
        return documents
