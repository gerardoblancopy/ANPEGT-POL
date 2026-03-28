"""News/RSS corpus source."""

import logging
from uuid import uuid4

from anpegt.schema.corpus import CorpusDocument

logger = logging.getLogger(__name__)


class NewsSource:
    """Fetches documents from RSS/Atom feeds using feedparser."""

    source_type: str = "news"

    def fetch(self, config: dict) -> list[CorpusDocument]:
        """Fetch documents from RSS feeds.

        Parameters
        ----------
        config:
            Must contain 'path_or_url' with the feed URL(s).
            Can be a single URL string or comma-separated URLs.

        Returns
        -------
        list[CorpusDocument]
            Ingested documents from feeds.
        """
        try:
            import feedparser
        except ImportError:
            logger.warning(
                "NewsSource: feedparser not installed. "
                "Install it with: pip install feedparser"
            )
            return []

        urls_raw = config.get("path_or_url", "")
        urls = [u.strip() for u in urls_raw.split(",") if u.strip()]
        source_id_prefix = config.get("id", "news")

        documents: list[CorpusDocument] = []

        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    title = getattr(entry, "title", "")
                    summary = getattr(entry, "summary", "")
                    content = ""
                    if hasattr(entry, "content") and entry.content:
                        content = entry.content[0].get("value", "")

                    raw_text = f"{title}\n\n{content or summary}"
                    metadata = {
                        "title": title,
                        "link": getattr(entry, "link", ""),
                        "published": getattr(entry, "published", ""),
                        "feed_url": url,
                        "feed_title": getattr(feed.feed, "title", ""),
                    }

                    entry_id = getattr(entry, "id", str(uuid4()))
                    documents.append(
                        CorpusDocument(
                            source_type=self.source_type,
                            source_id=f"{source_id_prefix}/{entry_id}",
                            raw_text=raw_text,
                            metadata=metadata,
                        )
                    )
            except Exception as exc:
                logger.warning("NewsSource: error fetching %s: %s", url, exc)

        logger.info(
            "NewsSource: fetched %d documents from %d feeds",
            len(documents),
            len(urls),
        )
        return documents
