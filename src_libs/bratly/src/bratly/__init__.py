# Extend namespace for bratly.io and bratly.eval subpackages
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .annotation_types import (
    Annotation,
    AttributeAnnotation,
    EntityAnnotation,
    EquivalenceAnnotation,
    EventAnnotation,
    Fragment,
    NormalizationAnnotation,
    NoteAnnotation,
    RelationAnnotation,
)
from .collection_types import (
    AnnotationCollection,
    Document,
    DocumentCollection,
)
from .exceptions import ParsingError
