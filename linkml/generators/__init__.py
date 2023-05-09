"""
Generators translate between a SchemaDefinition and an alternative
representation such as JsonSchema
"""
# Generator version numbers
__all__ = [
    "csvgen",
    "dotgen",
    "docgen",
    "golrgen",
    "graphqlgen",
    "javagen",
    "jsonldcontextgen",
    "jsonldgen",
    "jsonschemagen",
    "markdowngen",
    "namespacegen",
    "owlgen",
    "protogen",
    "pythongen",
    "djangogen",
    "rdfgen",
    "shexgen",
    "sssomgen",
    "summarygen",
    "yamlgen",
    "yumlgen",
    "PYTHON_GEN_VERSION",
]
GENERATOR_BASE = "0.9"

DJANGO_GEN_VERSION = GENERATOR_BASE + ".0"
PYTHON_GEN_VERSION = GENERATOR_BASE + ".0"
JAVA_GEN_VERSION = GENERATOR_BASE + ".0"
