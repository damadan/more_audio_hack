import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.title_normalizer import normalize_title


def test_ml_title_normalization():
    assert normalize_title("ML-инженер") == "Machine Learning Engineer"
