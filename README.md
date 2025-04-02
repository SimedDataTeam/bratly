# bratly

**bratly** is a simple Python library to create, manipulate, compare (collections of) annotated documents in [Brat standoff format](https://brat.nlplab.org/standoff.html)

## Why bratly ?

- a simpler, restricted set of existing brat objects/types
- fully serializable (pydantic-based)
- new instancied concepts: Document (txt + ann + metadata), DocumentCollection, AnnotationCollection, Fragment, with full-stack of utilities and tools

- It is composed of three packages:
  1. bratly ([docs](src_libs/bratly/src/bratly/README.md)): the core part with classes, defines classes of collections and annotations
  2. bratly_io_fs ([docs](src_libs/bratly_io_fs/src/bratly_io_fs/README.md)): read/write collections from/to files
  3. bratly_eval ([docs](src_libs/bratly_eval/src/bratly_eval/README.md)): compare/evaluate two sets of annotations (produce quantitative and qualitative evaluation)

## bratly classes

- Collection classes:
  - DocumentCollection: a set of documents (usually a set of txt + ann files stored in a folder)
    - Document : A document (usually txt + ann files), which can be linked to one or multiple AnnotationCollection
      - AnnotationCollection : a set of Annotations, one txt file can be linked to one or multiple AnnotationCollection (multiple versions, different annotation types...)

- Annotation classes:
  - EntityAnnotation : annotation of a text segment. Defined by a list of fragments (usually 1), the text content, and the label (category), as in ann file. e.g T1 Name 34 45 Santa Claus
  - RelationAnnotation : a relation between two EntityAnnotations.
  - AttributeAnnotation : an attribute linked to an EntityAnnotation
  - EventAnnotation
  - NormalizationAnnotation
  - NoteAnnotation
  - EquivalenceAnnotation

- Fragment : a fragment of text within an entity annotation. Defined by starting and ending character positions


## Getting started

 [Build annotations programmatically - first entities in a toy example](src_devs/bratly_eval_dev/src/bratly_eval_dev/notebooks/demo.ipynb)

## Contact
This work has been performed by the [Division of Medical Information Sciences (SIMED) from the University Hospitals of Geneva](https://www.hug.ch/sciences-de-linformation-medicale) whose contact details are available [here](https://www.hug.ch/sciences-de-linformation-medicale/infos-pratiques).