"""Corpus source protocol."""

from typing import Protocol, runtime_checkable

from anpegt.schema.corpus import CorpusDocument


@runtime_checkable
class CorpusSource(Protocol):
    source_type: str

    def fetch(self, config: dict) -> list[CorpusDocument]: ...
