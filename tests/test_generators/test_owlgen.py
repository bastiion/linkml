import sys
import unittest

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SlotDefinition
from rdflib import RDFS, SKOS, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF

from linkml.generators.owlgen import MetadataProfile, OwlSchemaGenerator
from linkml.utils.schema_builder import SchemaBuilder
from tests.test_generators.environment import env

SCHEMA = env.input_path("kitchen_sink.yaml")
DATA = env.input_path("kitchen_sink_inst_01.yaml")
SHEXLOG = env.expected_path("owl_log.txt")
OWL_OUTPUT = env.expected_path("kitchen_sink.owl.ttl")
OWL_OUTPUT_RDFS = env.expected_path("kitchen_sink.rdfs-profile.owl.ttl")
OWL_OUTPUT_TMP = env.expected_path("tmp.owl.ttl")

SYMP = Namespace("http://purl.obolibrary.org/obo/SYMP_")
KS = Namespace("https://w3id.org/linkml/tests/kitchen_sink/")
LINKML = Namespace("https://w3id.org/linkml/")
BIZ = Namespace("https://example.org/bizcodes/")


class OwlGeneratorTestCase(unittest.TestCase):
    """
    Tests generation of an OWL schema from a LinkML schema
    """

    def test_owlgen(self):
        """tests generation of owl schema-style ontologies"""
        owl = OwlSchemaGenerator(
            SCHEMA,
            mergeimports=False,
            metaclasses=False,
            type_objects=False,
            ontology_uri_suffix=".owl.ttl",
        ).serialize()
        with open(OWL_OUTPUT, "w") as stream:
            stream.write(owl)
        g = Graph()
        g.parse(OWL_OUTPUT, format="turtle")
        owl_classes = list(g.subjects(RDF.type, OWL.Class))
        self.assertGreater(len(owl_classes), 10)
        for c in owl_classes:
            types = list(g.objects(c, RDF.type))
            self.assertCountEqual(types, [OWL.Class])
        assert KS.MedicalEvent in owl_classes
        # test that enums are treated as classes
        assert KS.EmploymentEventType in owl_classes
        owl_object_properties = list(g.subjects(RDF.type, OWL.ObjectProperty))
        assert len(owl_object_properties) > 10
        for p in owl_object_properties:
            types = list(g.objects(p, RDF.type))
            self.assertCountEqual(types, [OWL.ObjectProperty])
        owl_datatype_properties = list(g.subjects(RDF.type, OWL.DatatypeProperty))
        assert len(owl_datatype_properties) > 10
        for p in owl_datatype_properties:
            types = list(g.objects(p, RDF.type))
            self.assertCountEqual(types, [OWL.DatatypeProperty])
        # check that definitions are present, and use the default profile
        self.assertIn(
            Literal("A person, living or dead"), g.objects(KS.Person, SKOS.definition)
        )
        # test enums
        enum_bnode = list(g.objects(KS.EmploymentEventType, OWL.unionOf))[0]
        coll = Collection(g, enum_bnode)
        self.assertCountEqual(
            [BIZ["001"], BIZ["002"], BIZ["003"], BIZ["004"]], list(coll)
        )
        assert BIZ["001"] in owl_classes

    def test_rdfs_profile(self):
        owl = OwlSchemaGenerator(
            SCHEMA,
            mergeimports=False,
            metaclasses=False,
            type_objects=False,
            metadata_profile=MetadataProfile.rdfs,
            ontology_uri_suffix=".owl.ttl",
        ).serialize(mergeimports=False)
        with open(OWL_OUTPUT_RDFS, "w") as stream:
            stream.write(owl)
        g = Graph()
        g.parse(OWL_OUTPUT_RDFS, format="turtle")
        owl_classes = list(g.subjects(RDF.type, OWL.Class))
        for c in owl_classes:
            # check not using the default metadata profile
            self.assertEqual([], list(g.objects(c, SKOS.definition)))
        # check that definitions are present, and use the RDFS profile
        self.assertIn(
            Literal("A person, living or dead"), g.objects(KS.Person, RDFS.comment)
        )

    def test_definition_uris(self):
        """
        Tests behavior of assigning URIs to classes and slots

        In future this will be paramterizable as per:
        https://github.com/linkml/linkml/issues/932
        """
        sb = SchemaBuilder()
        sb.add_class('MyPerson',
                     class_uri='schema:Person',
                     slots=[SlotDefinition("name", slot_uri="schema:name")])
        sb.add_defaults()
        sb.add_prefix("schema", "http://schema.org/")
        schema = sb.schema
        gen = OwlSchemaGenerator(schema, mergeimports=False, metaclasses=False, type_objects=False)
        owl = gen.serialize()
        with open(OWL_OUTPUT_TMP, "w", encoding="UTF-8") as stream:
            stream.write(owl)
        g = Graph()
        g.parse(OWL_OUTPUT_TMP)
        triples = list(g.triples((None,None,None)))
        expected = [
            (URIRef('http://example.org/test-schema/MyPerson'),
             URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'),
             URIRef('http://schema.org/Person'))
        ]
        for t in expected:
            self.assertIn(t, triples)


if __name__ == "__main__":
    unittest.main()
