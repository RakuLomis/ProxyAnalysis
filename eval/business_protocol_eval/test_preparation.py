import unittest
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np
from prepare import roles_for,verify_roles
from packages import Bundle,export
from common import PROTOCOLS,valid_w
from learning import schedule,independent_pre_schedule
from score import macro_f1,metrics


def cohort():
    return pd.DataFrame([{'session_id':f'{p}-{y}-{c}-{r}','protocol':p,'label_id':str(y),
                         'content_id':f'{y}-{c}','fold':c,'repetition':r}
                        for p in PROTOCOLS for y in range(6) for c in range(5) for r in range(1,5)])


class PreparationTests(unittest.TestCase):
    def test_scoring_six_class_and_pooled_not_protocol_average(self):
        y=np.arange(6);m,_=metrics(y,np.eye(6))
        self.assertEqual(m['F1'],1);self.assertEqual(m['CE_bits'],0);self.assertEqual(m['Brier'],0)
        a=np.eye(6)*3;b=np.zeros((6,6));b[:,0]=3
        self.assertNotAlmostEqual(float(macro_f1(a+b)),float((macro_f1(a)+macro_f1(b))/2))
    def test_joint_content_and_domain_holdout(self):
        c=cohort();role=roles_for(c,'E2',2,'vless');verify_roles(c,role,'E2',2,'vless')
        self.assertEqual([len(role[k]) for k in ['train','test','unused']],[384,24,192])
        bad={k:list(v) for k,v in role.items()}
        bad['train'][0]=c[c.protocol.eq('vless')&c.fold.eq(1)].iloc[0].session_id
        with self.assertRaises(AssertionError):verify_roles(c,bad,'E2',2,'vless')

    def test_invalid_W_not_clipped(self):
        valid_w([[5,7,2,2,1,1]])
        with self.assertRaises(AssertionError):valid_w([[1,7,2,2,1,1]])

    def test_capability_blocks_existing_files(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);export(p,{'post':pd.DataFrame({'x':[1]}),'test_post':pd.DataFrame({'x':[99]})},{})
            b=Bundle(p,'M0');self.assertEqual(b.get('post').x.tolist(),[1])
            with self.assertRaises(PermissionError):b.get('test_post')
            self.assertEqual(b.access,['post'])

    def test_pre_schedule_does_not_need_visit_ids(self):
        p=cohort();p=p[p.protocol.eq('vless')&p.fold.ne(0)].reset_index(drop=True)
        pre=p[['protocol','content_id','label_id']].sample(frac=1,random_state=3).reset_index(drop=True)
        ix=schedule(p,1,steps=8);px=independent_pre_schedule(p,pre,ix)
        np.testing.assert_array_equal(p.iloc[ix[0]].label_id.to_numpy(),pre.iloc[px[0]].label_id.to_numpy())


if __name__=='__main__':unittest.main()
