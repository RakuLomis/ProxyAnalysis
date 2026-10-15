"""Preserve and register a pre-score accounting fix, without resealing the model."""
from common import ROOT, OUT, read, write, relative, hash_file, require


def run():
    require(not (OUT/'scores/score-complete.json').exists(),'Repair is only authorized before first scoring')
    contract=read(OUT/'manifests/experiment-contract.json')
    changes={}
    for name in ['evaluate','uncertainty','fit']:
        old=OUT/'engineering/score-weight-repair-01'/(name+'.original.py')
        path=ROOT/'eval/protocol_probability_drift'/(name+'.py')
        rel=relative(path)
        require(hash_file(old)==contract['source_sha256'][rel],'Original source backup differs from seal')
        changes[rel]={'original_sha256':hash_file(old),'repaired_sha256':hash_file(path),'backup':relative(old)}
    write(OUT/'manifests/engineering-repairs.json',{
       'source_changes':changes,'reason':'retain evaluation mass when aggregating flow-equal content summaries',
       'discovered_before_first_test_score':True,'main_hierarchical_estimand_unchanged':True,
       'fit_code_logic_change':'only permit documented source hash repair on resumed integrity check',
       'kernel_formulas_or_models_changed':False,'member_or_fold_changes':False,
       'test_results_used_to_choose_repair':False,'original_contract_preserved':True})


if __name__=='__main__':run()
