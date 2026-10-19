"""AD1 isolated IO; inherit source/query/score capabilities and numerical guards."""
from pathlib import Path
_parent=Path(__file__).resolve().parents[2]/'eval/role_asymmetric_transfer_nr2_full/common.py'
exec(compile(_parent.read_text(encoding='utf-8'),str(_parent),'exec'),globals())
PARENT=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/full-nr2-01'
PARENT_CODE=ROOT/'eval/role_asymmetric_transfer_nr2_full'
OUT=ROOT/'outputs/role-asymmetric-transfer-v1-20261017/ad1-2x2-01'
DOC=ROOT/'docs/role-asymmetric-transfer-v1-20261017/ad1-2x2-01'
PLAN=ROOT/'plan/RA1-AD1-execution-contract-20261018.md'
