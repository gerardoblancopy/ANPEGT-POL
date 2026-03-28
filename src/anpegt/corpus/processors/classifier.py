"""Topic classifier for corpus documents."""

from anpegt.schema.config import ClusterDef, VoterSegmentDef


class KeywordClassifier:
    """Classifies text into clusters and voter segments using keyword matching."""

    def __init__(self, clusters: list[ClusterDef]) -> None:
        self.clusters = clusters

    def classify(self, text: str) -> list[str]:
        """Return cluster IDs whose keywords match in the text (case-insensitive).

        Parameters
        ----------
        text:
            The text to classify.

        Returns
        -------
        list[str]
            List of matching cluster IDs.
        """
        text_lower = text.lower()
        matched: list[str] = []
        for cluster in self.clusters:
            for keyword in cluster.keywords:
                if keyword.lower() in text_lower:
                    matched.append(cluster.id)
                    break
        return matched

    def classify_segment(
        self, text: str, segments: list[VoterSegmentDef]
    ) -> list[str]:
        """Return segment IDs whose priority_issues match in the text.

        Parameters
        ----------
        text:
            The text to classify.
        segments:
            List of voter segment definitions.

        Returns
        -------
        list[str]
            List of matching segment IDs.
        """
        text_lower = text.lower()
        matched: list[str] = []
        for segment in segments:
            for issue in segment.priority_issues:
                if issue.lower() in text_lower:
                    matched.append(segment.id)
                    break
        return matched
