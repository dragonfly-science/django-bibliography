from django.utils import unittest
from bibliography.models import Reference

erdos = """@article{erdos1960evolution,
  title={$\{$On the evolution of random graphs$\}$},
  author={Erdos, P. and R{\'e}nyi, A.},
  journal={Publ. Math. Inst. Hung. Acad. Sci},
  volume={5},
  pages={17--61},
  year={1960}
}"""

class ReferenceTestCase(unittest.TestCase):
    def setUp(self):
        self.reference = Reference.objects.create(bibtex=erdos)
        self.reference.save()

    def test_name(self):
        self.assertEqual(self.name, 'erdos1960evolution')


