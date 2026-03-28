"""Source registry for corpus ingestion."""

import logging
from typing import Any

from anpegt.corpus.base import CorpusSource
from anpegt.corpus.sources.local_files import LocalFilesSource
from anpegt.corpus.sources.news import NewsSource
from anpegt.corpus.sources.social_media import SocialMediaSource
from anpegt.corpus.sources.audio import AudioTranscriptionSource
from anpegt.corpus.sources.interviews import InterviewsSource
from anpegt.corpus.sources.opposition import OppositionSource
from anpegt.corpus.sources.parliament import ParliamentSource
from anpegt.corpus.sources.surveys import SurveysSource
from anpegt.corpus.sources.focus_groups import FocusGroupsSource
from anpegt.corpus.sources.territorial import TerritorialSource
from anpegt.corpus.sources.media_monitor import MediaMonitorSource

logger = logging.getLogger(__name__)


class SourceRegistry:
    """Registry mapping source_type strings to CorpusSource implementations."""

    def __init__(self) -> None:
        self._sources: dict[str, type] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all built-in source implementations."""
        defaults: list[type] = [
            LocalFilesSource,
            NewsSource,
            SocialMediaSource,
            AudioTranscriptionSource,
            InterviewsSource,
            OppositionSource,
            ParliamentSource,
            SurveysSource,
            FocusGroupsSource,
            TerritorialSource,
            MediaMonitorSource,
        ]
        for source_cls in defaults:
            self._sources[source_cls.source_type] = source_cls

    def register(self, source_type: str, source_cls: type) -> None:
        """Register a custom source implementation.

        Parameters
        ----------
        source_type:
            The source type identifier.
        source_cls:
            The class implementing the CorpusSource protocol.
        """
        self._sources[source_type] = source_cls

    def get_source(self, source_type: str) -> CorpusSource:
        """Get an instance of the source for the given type.

        Parameters
        ----------
        source_type:
            The source type identifier.

        Returns
        -------
        CorpusSource
            An instance of the matching source.

        Raises
        ------
        KeyError
            If the source_type is not registered.
        """
        if source_type not in self._sources:
            raise KeyError(
                f"Unknown source type: {source_type!r}. "
                f"Available: {list(self._sources.keys())}"
            )
        return self._sources[source_type]()

    def available_types(self) -> list[str]:
        """Return list of all registered source types."""
        return list(self._sources.keys())
