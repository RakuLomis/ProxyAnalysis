"""Bind the sealed full NR2 numerical policy without changing its body."""
from pathlib import Path
_source=Path(__file__).resolve().parents[2]/'eval/role_asymmetric_transfer_nr2_full/numeric_policy.py'
exec(compile(_source.read_text(encoding='utf-8'),str(_source),'exec'),globals())
