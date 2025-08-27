import numpy as np

from hr_match_mcp.scoring import combine_score, must_have_covered, read_yaml_config


def test_must_have_semantic_and_weights():
    vecs = {
        "gcp": np.array([1.0, 0.0]),
        "google cloud": np.array([0.9, 0.1]),
        "aws": np.array([0.0, 1.0]),
    }
    covered, _ = must_have_covered(["gcp"], ["google cloud"], vecs, 0.8)
    assert covered
    covered2, _ = must_have_covered(["gcp"], ["aws"], vecs, 0.8)
    assert not covered2

    cfg = read_yaml_config()
    score = combine_score(1.0, 1.0, 1.0, 0.0, cfg["weights"])
    assert score == 100.0
