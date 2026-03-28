"""Audio transcription corpus source."""

import logging
from pathlib import Path

from anpegt.schema.corpus import CorpusDocument

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}


def _parse_yaml_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from text if present."""
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


class AudioTranscriptionSource:
    """Transcribes audio files or reads pre-existing transcriptions."""

    source_type: str = "audio"

    def fetch(self, config: dict) -> list[CorpusDocument]:
        """Fetch transcription documents.

        If faster-whisper is available, transcribes audio files directly.
        Otherwise, reads pre-existing .txt transcriptions from the path.

        Parameters
        ----------
        config:
            Must contain 'path_or_url' pointing to a directory.

        Returns
        -------
        list[CorpusDocument]
            Transcribed documents.
        """
        path = Path(config.get("path_or_url", ""))
        if not path.is_dir():
            logger.warning(
                "AudioTranscriptionSource: path %s is not a directory", path
            )
            return []

        source_id_prefix = config.get("id", "audio")

        # Try to use faster-whisper for audio transcription
        whisper_available = False
        try:
            from faster_whisper import WhisperModel

            whisper_available = True
        except ImportError:
            logger.info(
                "AudioTranscriptionSource: faster-whisper not available, "
                "reading pre-existing transcriptions only"
            )

        documents: list[CorpusDocument] = []

        if whisper_available:
            documents.extend(
                self._transcribe_audio(path, source_id_prefix)
            )

        # Always also read pre-existing .txt transcriptions
        documents.extend(
            self._read_transcriptions(path, source_id_prefix)
        )

        logger.info(
            "AudioTranscriptionSource: fetched %d documents from %s",
            len(documents),
            path,
        )
        return documents

    def _transcribe_audio(
        self, path: Path, source_id_prefix: str
    ) -> list[CorpusDocument]:
        """Transcribe audio files using faster-whisper."""
        from faster_whisper import WhisperModel

        documents: list[CorpusDocument] = []
        model = WhisperModel("base", device="cpu")

        for filepath in sorted(path.iterdir()):
            if filepath.suffix.lower() not in AUDIO_EXTENSIONS:
                continue
            try:
                segments, info = model.transcribe(str(filepath))
                text = " ".join(seg.text for seg in segments)
                documents.append(
                    CorpusDocument(
                        source_type=self.source_type,
                        source_id=f"{source_id_prefix}/{filepath.name}",
                        raw_text=text,
                        metadata={
                            "filename": filepath.name,
                            "language": info.language,
                            "duration": info.duration,
                            "transcription_method": "faster-whisper",
                        },
                    )
                )
            except Exception as exc:
                logger.warning(
                    "AudioTranscriptionSource: error transcribing %s: %s",
                    filepath,
                    exc,
                )

        return documents

    def _read_transcriptions(
        self, path: Path, source_id_prefix: str
    ) -> list[CorpusDocument]:
        """Read pre-existing .txt transcription files."""
        documents: list[CorpusDocument] = []

        for filepath in sorted(path.glob("*.txt")):
            try:
                raw = filepath.read_text(encoding="utf-8")
                metadata, body = _parse_yaml_frontmatter(raw)
                metadata["filename"] = filepath.name
                metadata.setdefault("transcription_method", "pre-existing")

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
                    "AudioTranscriptionSource: error reading %s: %s",
                    filepath,
                    exc,
                )

        return documents
