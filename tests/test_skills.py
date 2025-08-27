from hr_match_mcp.models import HRModels
from hr_match_mcp.parsing import extract_skills
from hr_match_mcp.scoring import read_yaml_config


def test_skill_normalization_and_semantics():
    models = HRModels()
    cfg = read_yaml_config()
    text = "We use torch, k8s, Postgre and Big Query extensively."
    skills = extract_skills(text, models, cfg)
    assert "pytorch" in skills
    assert "kubernetes" in skills
    assert "postgresql" in skills
    assert "gcp" in skills
