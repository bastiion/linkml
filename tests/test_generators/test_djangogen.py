import unittest
from pathlib import Path
from types import ModuleType
from typing import Optional

from linkml.generators.djangogen import DjangoGenerator
from tests.test_generators.environment import env
from tests.test_generators.djangoapp.settings import pre_test_stage

SCHEMA = env.input_path("simple.yaml")
PYTHON = Path("djangoapp/models.py")


def classesinmodule(module):
    md = module.__dict__
    return [
        md[c] for c in md if (
                isinstance(md[c], type) and md[c].__module__ == module.__name__
        )
    ]
def make_python(infile, outfile, save: Optional[bool] = False) -> ModuleType:
    """
    Note: if you change the yaml schema and associated test instance objects,
    you may need to run this test twice
    """
    pstr = str(DjangoGenerator(infile, mergeimports=True).serialize())
    if save:
        with open(outfile, "w") as io:
            io.write(pstr)


class DjangoGenTestCase(unittest.TestCase):
    def test_pythongen(self):
        """python"""
        pre_test_stage("djangoapp")
        make_python(SCHEMA, PYTHON, True)
        import djangoapp.models as kitchen_module
        cls =  classesinmodule(kitchen_module)
        self.assertEqual(len(cls), 4)



if __name__ == "__main__":
    unittest.main()
