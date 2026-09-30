"""Seal scientific/permission preparation; production execution remains a later stage."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from proxy_analysis.extend_calibration.audit import read,write,file_hash
NEW=ROOT/'outputs/extend-calibration-20260930/run-01/extraction-03'
PREP=NEW/'training-preparation-01'


def main():
    target=PREP/'preregistration.json';assert not target.exists()
    gates=[NEW/'full-gate.json',NEW/'clock-anchors-01/summary.json',NEW/'verification-01/verification.json',
           NEW/'identity-source-evidence/qualification.json',PREP/'package-gate.json',PREP/'cuda-smoke.json']
    assert read(gates[0])['W_passed']==600 and read(gates[1])['bracket_failed']==0
    assert read(gates[2])['independent_event_counts'] and read(gates[3])['qualified_for_registered_entity_grouping']
    assert read(gates[4])['passed'] and read(gates[5])['passed']
    manifests=list((PREP/'packages').glob('*/*/manifest.json'));assert len(manifests)==4320
    sources=list((ROOT/'src/proxy_analysis/extend_calibration').glob('*.py'))+list((ROOT/'eval/extend_calibration').glob('*.py'))
    contract={'version':'extend-common-window-3','preparation_passed':True,'formal_training_authorized':False,
        'subjects':{'visits':600,'contents':30,'businesses':6,'repetitions':[1,2,3,4],'Hy2':'measurement_only'},
        'tracks':{'W':{'protocols':['shadowsocks','vless','trojan','vmess','anytls'],'features':6,'scenarios':600},
                  'T':{'protocols':['shadowsocks','vless','trojan','vmess'],'features':7,'scenarios':480}},
        'scenario':{'outer_content_folds':5,'new_business_groups':3,'calibration_rotations':8,
                    'C_contents':6,'C_visits':24,'U_contents':18,'U_visits':72,'H_contents':6,'H_visits':24},
        'arms':['raw','center','marginal','paired','cyclic','group'],
        'reference_stage':'real U_post only after restricted prediction seal',
        'learning':{'seeds':[20260918,20260919,20260920],'synthetic_views_per_U_visit':8,
                    'classifier_hidden':32,'classes':6,'steps':1000,'batch':24,'learning_rate':.001,
                    'cuda_required':True,'restricted_classifier_fits':19440,'reference_classifier_fits':3240},
        'statistics':{'primary_contrasts':['paired-raw','paired-group'],'endpoint':'F1_new computed from full six-class confusion matrix',
                      'W_primary_family':10,'T_primary_family':8,'bootstrap_draws':10000,
                      'cluster':'canonical content, business-stratified; preserve cross-protocol dependence',
                      'ordinary_CI':.95,'W_family_CI':.995,'T_family_CI':.99375,
                      'success':'both family-adjusted lower bounds > 0 per deployment',
                      'practical_reference_percentage_points':1},
        'source_hashes':{str(p.relative_to(ROOT)):file_hash(p) for p in sources+gates+[NEW/'contract.json',PREP/'roles.parquet']},
        'package_manifest_hashes':{str(p.relative_to(ROOT)):file_hash(p) for p in manifests},
        'remaining':'port/freeze production generation, independent batched classifiers and scoring workers before formal run; no threshold/subset search',
        'full_TCP_birth_reconstruction_claimed':False,'OS_sandbox_security_claimed':False}
    write(target,contract)
    print({'preparation_passed':True,'formal_classifier_budget':22680,'formal_training_authorized':False})


if __name__=='__main__':main()
