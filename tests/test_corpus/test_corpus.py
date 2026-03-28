"""Tests for corpus processing."""

from anpegt.corpus.processors.cleaner import clean_text
from anpegt.corpus.processors.chunker import chunk_text
from anpegt.corpus.processors.classifier import KeywordClassifier
from anpegt.schema.config import ClusterDef, VoterSegmentDef


def test_clean_text_html():
    result = clean_text("<p>Texto <b>importante</b></p>")
    assert "<p>" not in result
    assert "importante" in result


def test_clean_text_whitespace():
    result = clean_text("  Mucho   espacio   aquí  ")
    assert "  " not in result
    assert result.startswith("Mucho")


def test_chunk_text():
    text = "A" * 1000
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 250  # chunk_size + some tolerance


def test_chunk_text_short():
    text = "Texto corto"
    chunks = chunk_text(text, chunk_size=500)
    assert len(chunks) == 1
    assert chunks[0] == "Texto corto"


def test_keyword_classifier():
    clusters = [
        ClusterDef(id="salud", name="Salud", description="", keywords=["salud", "hospital"]),
        ClusterDef(id="educacion", name="Educación", description="", keywords=["educación", "escuela"]),
    ]
    classifier = KeywordClassifier(clusters)
    result = classifier.classify("El sistema de salud necesita más hospitales")
    assert "salud" in result


def test_keyword_classifier_no_match():
    clusters = [
        ClusterDef(id="salud", name="Salud", description="", keywords=["salud"]),
    ]
    classifier = KeywordClassifier(clusters)
    result = classifier.classify("El clima está cambiando")
    assert len(result) == 0


def test_classify_segment():
    segments = [
        VoterSegmentDef(
            id="seg_a", name="A", description="", size_fraction=0.5,
            priority_issues=["salud", "clima"], initial_embedding_seed="",
        ),
    ]
    clusters = [ClusterDef(id="x", name="X", description="", keywords=[])]
    classifier = KeywordClassifier(clusters)
    result = classifier.classify_segment("La salud pública es prioridad", segments)
    assert "seg_a" in result
