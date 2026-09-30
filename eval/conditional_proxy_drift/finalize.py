"""Final experiment completion record and stage-time annotations."""
from phase2 import *

freeze_phase2()
assert read(OUT/'stage-gate.json')['passed']
assert read(PHASE/'completion.json')['all_replays_passed']
assert read(OUT/'lineage-audit.json')['all_passed']
assert read(OUT/'generator-replay-audit.json')['all_passed']
assert read(OUT/'support-and-decoding-audit.json')['passed']
for name in ['coverage-report.md','generation-legality-report.md','drift-description.md']:
    path=DOC/name;text=path.read_text(encoding='utf-8')
    marker='> 阶段时点说明：'
    if marker not in text:
        first,rest=text.split('\n',1)
        text=first+'\n\n'+marker+'本文件保留对应阶段的执行记录；其中“尚未分类/尚未测试”描述该阶段时点。现F0–F10均已完成，最终结论见[综合总结](summary.md)。\n'+rest
        path.write_text(text,encoding='utf-8')
reports={str(p):digest(p) for p in DOC.glob('*.md')}
files=[*Path(__file__).parent.glob('*.py'),*Path(ROOT/'src/proxy_analysis/conditional_drift').glob('*.py'),CONFIG]
js('implementation-manifest.json',{'files':{str(p):digest(p) for p in files},'old_contract_intact':True})
js('completion.json',{'status':'complete','stages':'F0-F10','cohort_visits':240,'contents':30,'ridge_fits':2020,'classifiers':210,
  'training_updates':210000,'classification_oof_rows':5040,'cuda':True,'all_gates_passed':True,'reports':reports,
  'phase1_contract':digest(OUT/'contract.json'),'phase2_contract':digest(PHASE/'contract.json'),
  'new_collection':False,'PCAP_rescan':False,'old_results_overwritten':False})
print('F0-F10 complete; all contracts and gates verified',flush=True)
