"""Social media corpus source."""

import json
import logging
from pathlib import Path

from anpegt.schema.corpus import (
    CorpusDocument,
    EngagementMetrics,
    SocialMediaDocument,
)

logger = logging.getLogger(__name__)


class SocialMediaSource:
    """Reads social media JSON exports from a local directory."""

    source_type: str = "social_media"

    def fetch(self, config: dict) -> list[CorpusDocument]:
        """Fetch social media documents from JSON exports.

        Expected format per JSON file: a list of objects with fields:
        - text: str
        - platform: str
        - date: str
        - likes: int
        - comments: int
        - shares: int
        - reach: int
        - audience_comments: list[str] (optional)

        Parameters
        ----------
        config:
            Must contain 'path_or_url' pointing to a directory.

        Returns
        -------
        list[CorpusDocument]
            Ingested SocialMediaDocument instances.
        """
        path = Path(config.get("path_or_url", ""))
        if not path.is_dir():
            logger.warning(
                "SocialMediaSource: path %s is not a directory", path
            )
            return []

        source_id_prefix = config.get("id", "social_media")
        documents: list[CorpusDocument] = []

        for filepath in sorted(path.glob("*.json")):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    data = [data]

                for idx, item in enumerate(data):
                    text = item.get("text", "")
                    platform = item.get("platform", "unknown")
                    date = item.get("date", "")
                    likes = item.get("likes", 0)
                    comments_count = item.get("comments", 0)
                    shares = item.get("shares", 0)
                    reach = item.get("reach", 0)
                    audience_comments = item.get("audience_comments", [])

                    # Calculate engagement rate
                    total_engagement = likes + comments_count + shares
                    eng_rate = (
                        total_engagement / reach if reach > 0 else 0.0
                    )

                    engagement = EngagementMetrics(
                        likes=likes,
                        comments=comments_count,
                        shares=shares,
                        reach=reach,
                        engagement_rate=eng_rate,
                    )

                    doc = SocialMediaDocument(
                        source_type=self.source_type,
                        source_id=f"{source_id_prefix}/{filepath.stem}_{idx}",
                        raw_text=text,
                        platform=platform,
                        engagement=engagement,
                        audience_comments=audience_comments,
                        metadata={
                            "date": date,
                            "filename": filepath.name,
                        },
                    )
                    documents.append(doc)
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning(
                    "SocialMediaSource: error reading %s: %s",
                    filepath,
                    exc,
                )

        logger.info(
            "SocialMediaSource: fetched %d documents from %s",
            len(documents),
            path,
        )
        return documents
