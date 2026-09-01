from pathlib import Path

import pytest
import yaml

from proxy_analysis.config import ConfigError, FeatureConfig


CONFIG_PATH = Path("configs/feature-defaults.yaml")


def test_default_config_is_valid_and_hash_is_stable() -> None:
    first = FeatureConfig.load(CONFIG_PATH)
    second = FeatureConfig.load(CONFIG_PATH)
    assert first.schema_version == 1
    assert first.epsilon == 1.0
    assert first.sha256 == second.sha256
    assert len(first.sha256) == 64


def test_unknown_field_is_rejected(tmp_path: Path) -> None:
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    raw["surprise"] = True
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown top-level"):
        FeatureConfig.load(path)


def test_hysteria2_logical_post_cannot_be_enabled(tmp_path: Path) -> None:
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    raw["pairing"]["allow_hysteria2_logical_post"] = True
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ConfigError, match="forbidden"):
        FeatureConfig.load(path)

