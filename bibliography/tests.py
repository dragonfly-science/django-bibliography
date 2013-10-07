import os

from django.test import TestCase

from bibliography.models import Reference

fluff="""@article{steinhauser2009nature,
title={The nature of navel fluff},
author={Steinhauser, G.},
journal={Medical hypotheses},
volume={72},
number={6},
pages={623--625},
year={2009},
abstract={Hard facts on a soft matter! In their popular scientific book
(Leyner M, Goldberg B. Why do men have nipples - hundreds of questions you'd
only ask a doctor after your third martini. New York: Three Rivers Press;
2005), Leyner and Goldberg raised the question why "some belly buttons collect
so much lint". They were, however, not able to come up with a satisfactory
answer. The hypothesis presented herein says that abdominal hair is mainly
responsible for the accumulation of navel lint, which, therefore, this is a
typically male phenomenon. The abdominal hair collects fibers from cotton
shirts and directs them into the navel where they are compacted to a felt-like
matter. The most abundant individual mass of a piece of lint was found to be
between 1.20 and 1.29 mg (n=503). However, due to several much larger pieces,
the average mass was 1.82 mg in this three year study. When the abdominal hair
is shaved, no more lint is collected. Old T-shirts or dress shirts produce less
navel fuzz than brand new T-shirts. Using elemental analysis, it could be shown
that cotton lint contains a certain amount of foreign material, supposedly
cutaneous scales, fat or proteins. Incidentally, lint might thus fulfill a
cleaning function for the navel.} 
}"""

erdos ="""@inproceedings{bollobas1976cliques,
  title={Cliques in random graphs},
  author={Bollob{\'a}s, B. and Erdos, P.},
  booktitle={Mathematical Proceedings of the Cambridge Philosophical Society},
  volume={80},
  number={03},
  pages={419--427},
  year={1976}
}"""

csl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apa.csl') 
html = u'<p>Steinhauser, G. (2009). The nature of navel fluff. <em>Medical hypotheses</em>, <em>72</em>(6), 623\u2013625.</p>\n'

class AccentTestCase(TestCase):
    def test_accent(self):
        reference = Reference(bibtex=erdos)
        self.assertEqual(reference.get_authors(), u'B Bollob\u2019as & P Erdos')

class SingleReferenceTestCase(TestCase):
    def setUp(self):
        self.reference = Reference(bibtex=fluff)
        self.reference.save()

    def test_key(self):
        """Check that the key can be extracted"""
        self.assertEqual(self.reference.key, 'steinhauser2009nature')

    def test_year(self):
        """Check that the year can be extracted"""
        self.assertEqual(self.reference.get_year(), 2009)

    def test_title(self):
        """Check that the title can be extracted"""
        self.assertEqual(self.reference.get_title(), "The nature of navel fluff")

    def test_authors(self):
        """Check that authors can be extracted"""
        self.assertIn('Steinhauser', self.reference.get_authors())
    
    def test_html(self):
        """Check that the html is output correctly"""
        self.assertEqual(self.reference.get_html(csl=csl), html)

    def test_abstract(self):
        """Check that the abstract is returned"""    
        self.assertIn('lint', self.reference.get_abstract())
        self.assertIn('Why do men have nipples', self.reference.get_abstract())
