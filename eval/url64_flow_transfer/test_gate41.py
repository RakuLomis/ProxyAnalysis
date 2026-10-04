import unittest
from review41_gate import proposed_entities
from prepare41 import path_identity


class GateTests(unittest.TestCase):
    def test_unambiguous_path_only(self):
        p={'network':'tcp','src_ip':'192.0.2.1','src_port':1,'dst_ip':'192.0.2.2','dst_port':2}
        r={'path_hash':path_identity(p),'positive_packets':1,'syn_count':1,'entity_ids':['a'],'bad_packets':0}
        self.assertEqual(proposed_entities({'a':[p]},[r]),{'a'})
        for field,value in [('syn_count',0),('syn_count',2),('entity_ids',['a','b']),('bad_packets',1),('positive_packets',0)]:
            self.assertEqual(proposed_entities({'a':[p]},[{**r,field:value}]),set())


if __name__=='__main__':unittest.main()
