from proxy_analysis.crosscontent.business_conservative import match_training
from proxy_analysis.crosscontent.business_splits import teacher_assignment, donors


def test_missing_round_removes_counterpart_for_all_student_arms():
    rows=[{'session_id':f'{label}-{content}-{repeat}','label_id':label,
           'content_id':f'{label}:{content}','protocol':'SHADOWSOCKS','repetition':repeat}
          for label in ('a','b') for content in range(4) for repeat in range(1,6)
          if not(label=='a' and content==0 and repeat==3)]
    assert len(rows)==39
    for scheme in range(3):
        partitions=teacher_assignment(rows,scheme)
        matched=match_training(rows,partitions)
        assert len(matched)==38
        assert len({r['session_id'] for r in matched})==38
        mapping=donors(matched,partitions)
        assert sorted(mapping)==list(range(38))
        assert all(matched[i]['repetition']==matched[j]['repetition'] for i,j in enumerate(mapping))
        removed={r['session_id'] for r in rows}-{r['session_id'] for r in matched}
        assert len(removed)==1
        assert next(iter(removed)).startswith('a-')


def test_complete_pool_keeps_fifth_round():
    rows=[{'session_id':f'{c}-{r}','label_id':'a','content_id':str(c),
           'protocol':'VLESS','repetition':r} for c in range(4) for r in range(1,6)]
    assert match_training(rows,teacher_assignment(rows,0))==rows
