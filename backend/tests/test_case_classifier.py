# tests/test_case_classifier.py
from app.services.case_classifier import classify_case


def test_simple_case_no_children_no_assets():
    data = {
        "has_children": "não",
        "has_assets": "não",
    }
    assert classify_case(data) == "simple"


def test_complex_case_with_children():
    data = {
        "has_children": "sim, 2 filhos de 5 e 8 anos",
        "has_assets": "não",
    }
    assert classify_case(data) == "complex"


def test_complex_case_with_assets():
    data = {
        "has_children": "não",
        "has_assets": "sim, apartamento no centro",
    }
    assert classify_case(data) == "complex"


def test_complex_case_with_both():
    data = {
        "has_children": "sim",
        "has_assets": "sim",
    }
    assert classify_case(data) == "complex"


def test_simple_when_fields_missing():
    assert classify_case({}) == "simple"
