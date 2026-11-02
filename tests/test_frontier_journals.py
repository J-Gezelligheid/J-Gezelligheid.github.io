import importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('journals',Path(__file__).resolve().parents[1]/'scripts/update_frontier_journals.py')
u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
class IssueSafety(unittest.TestCase):
 def test_nonresearch_removed(self):
  for title in [' Front Matter\n','Backmatter of Econometrica','Recent Referees','JPE Turnaround Times']:
   self.assertFalse(u.research(title))
  self.assertTrue(u.research('The Employment Effects of a Guaranteed Income'))
 def test_partial_directory_rejected(self):
  issue={'id':'qje','volume':141,'issue':4,'expected_count':2}
  with patch.object(u,'load',return_value={'message':{'items':[{'title':['One paper'],'DOI':'10.1/x','volume':'141','issue':'4'}]}}):
   with self.assertRaises(ValueError):u.records(issue,Path('.'),True)
 def test_early_online_date_not_excluded(self):
  issue={'id':'qje','volume':141,'issue':4,'expected_count':1,'name':'QJE','year':2026}
  with patch.object(u,'load',return_value={'message':{'items':[{'title':['Early online'],'DOI':'10.1/x','volume':'141','issue':'4','published':{'date-parts':[[2025,1]]}}]}}):
   self.assertEqual(len(u.records(issue,Path('.'),True)),1)
if __name__=='__main__':unittest.main()