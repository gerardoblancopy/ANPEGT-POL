"""Tests for InMemoryVectorStore."""

import numpy as np


def test_add_and_query(vector_store):
    vector_store.add("v1", [1.0, 0.0, 0.0])
    vector_store.add("v2", [0.0, 1.0, 0.0])
    vector_store.add("v3", [0.9, 0.1, 0.0])

    results = vector_store.query([1.0, 0.0, 0.0], top_k=2)
    assert len(results) == 2
    # v1 should be most similar to query
    assert results[0][0] == "v1"
    assert results[0][1] > 0.99


def test_get_vector(vector_store):
    vector_store.add("v1", [1.0, 2.0, 3.0])
    vec = vector_store.get_vector("v1")
    assert vec is not None
    np.testing.assert_allclose(vec, [1.0, 2.0, 3.0])


def test_empty_query(vector_store):
    results = vector_store.query([1.0, 0.0, 0.0])
    assert results == []


def test_len(vector_store):
    assert len(vector_store) == 0
    vector_store.add("v1", [1.0, 0.0])
    assert len(vector_store) == 1
