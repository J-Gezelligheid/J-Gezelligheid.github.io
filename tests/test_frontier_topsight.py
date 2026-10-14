import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('updater', ROOT/'scripts/update_frontier_topsight.py')
u=importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class FrontierSafetyTests(unittest.TestCase):
    def setUp(self):
        self.old={'updated_at':'2026-03-06T00:00:00Z',
                  'journals':[{'name':name,'papers':[{'title_en':'Existing paper'}]} for name in u.PLAN['journals']],
                  'nber':{'papers':[{'title_en':'Existing NBER paper'}]}}
        self.paper={'paper_key':'a','title_en':'Wage policy','title_cn':'工资政策','authors':['Author'],
                    'year':2026,'source_lane':'working','source_id':'TEST:1','source_url':'https://example.org/paper',
                    'abstract_en':'Abstract','summary_cn':'导读'}
        self.batch={'retrieved_at':'2026-10-14T00:00:00Z','queries':[{'topic':'labor','response':{
            'ok':True,'lanes':{'working':{'status':'complete','items':[self.paper]}}}}]}
        self.selection={'reviewed':True,'topics':{'labor':['a']}}

    def test_failed_update_preserves_content_and_success_dates(self):
        first=u.merge(self.old,self.batch,self.selection)
        failed={'retrieved_at':'2026-11-01T00:00:00Z','queries':[{'topic':'labor','response':{'ok':False}}]}
        result=u.merge(first,failed,{'reviewed':True,'topics':{}})
        self.assertEqual(result['updated_at'],first['updated_at'])
        self.assertEqual(result['working']['topics'][0]['papers'],first['working']['topics'][0]['papers'])
        self.assertEqual(result['working']['topics'][0]['updated_at'],first['working']['topics'][0]['updated_at'])
        self.assertEqual(result['journals'][0]['updated_at'],self.old['updated_at'])

    def test_unknown_or_unreviewed_selection_rejected(self):
        for selection in [{'reviewed':False}, {'reviewed':True,'topics':{'labor':['invented']}}]:
            with self.assertRaises(ValueError): u.merge(self.old,self.batch,selection)

    def test_failed_lane_cannot_publish_its_items(self):
        self.batch['queries'][0]['response']['lanes']['working']['status']='failed'
        with self.assertRaises(ValueError): u.merge(self.old,self.batch,self.selection)

    def test_duplicate_across_topics_rejected(self):
        self.selection['topics']['macro']=['a']
        with self.assertRaises(ValueError): u.merge(self.old,self.batch,self.selection)

    def test_credentials_and_unsafe_urls_never_copied(self):
        self.paper.update(source_url='javascript:alert(1)', api_key='private-placeholder',client={'id':'private'})
        result=u.merge(self.old,self.batch,self.selection)['working']['topics'][0]['papers'][0]
        self.assertEqual(result['url'],'')
        self.assertNotIn('api_key',result)
        self.assertNotIn('client',result)

    def test_future_metadata_requires_review(self):
        self.paper['publication_date']='2027-01-01'
        with self.assertRaises(ValueError): u.merge(self.old,self.batch,self.selection)

    def test_wrong_journal_cannot_replace_top_five(self):
        self.paper.update(source_lane='formal',journal='Different Journal')
        lanes=self.batch['queries'][0]['response']['lanes']
        lanes['formal']=lanes.pop('working')
        self.selection={'reviewed':True,'topics':{},'journals':{'American Economic Review':['a']}}
        with self.assertRaises(ValueError): u.merge(self.old,self.batch,self.selection)

    def test_old_nber_and_input_unchanged(self):
        before=copy.deepcopy(self.old)
        result=u.merge(self.old,self.batch,self.selection)
        self.assertEqual(self.old,before)
        self.assertEqual(result['nber']['papers'],before['nber']['papers'])


if __name__=='__main__': unittest.main()
