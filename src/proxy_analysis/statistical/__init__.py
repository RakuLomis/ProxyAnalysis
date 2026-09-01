"""Reproducible statistical analysis over URL-aligned feature tables."""

from .config import StatisticalConfig
from .marts import build_statistical_marts

__all__ = ["StatisticalConfig", "build_statistical_marts"]
