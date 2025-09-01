from os import makedirs
from os.path import join

from bratly import AnnotationCollection, Document, DocumentCollection, EntityAnnotation
from bratly_io_fs import read_and_load_ann_file, read_and_load_txt_file, read_document_collection_from_folder, write_ann_file, write_ann_files_in_folder


def main():
    # Test: reading ann file and AnnotationCollection features
    print(
        "###################################################### CLASS AnnotationCollection ######################################################",
    )
    output_test = join(".", "dev_test", "io_fs_output")
    makedirs(output_test, exist_ok=True)
    annot_col = read_and_load_ann_file(join("data", "demo", "ann", "myannfile2.ann"))
    assert type(annot_col) is AnnotationCollection
    print(annot_col)
    print(annot_col.annotations)
    annot_col = read_and_load_ann_file(join("data", "demo", "ann", "myannfile3.ann"))
    assert type(annot_col) is AnnotationCollection
    print(annot_col)
    print(annot_col.annotations)
    annot_col = read_and_load_ann_file(
        "data/demo/ann/myannfile.ann",
        sorting=False,
        no_duplicates=False,
    )
    assert type(annot_col) is AnnotationCollection
    print(annot_col)
    print(annot_col.annotations)
    annot_col.sort_annotations()
    print("After sorting")
    print(annot_col.annotations)
    print("Finally we can write the AnnotationCollection as an ann file")
    write_ann_file(annot_col, join(output_test, "devtest_annfile.ann"))

    # Test: reading txt file with corresponding ann file
    print(
        "\n\n###################################################### CLASS Document ######################################################",
    )
    print("Reading Document 1 with ann path given:")
    document = read_and_load_txt_file(
        txtpath=join("data", "demo", "txt", "myannfile.txt"),
        annpath=join("data", "demo", "ann", "myannfile.ann"),
        ann_sorting=False,
        ann_no_duplicates=False,
    )
    assert type(document) is Document
    print(document)
    print("Folder path:", document.folderpath)
    print(
        "Filename without ext path:",
        document.filename_without_ext,
        "and extension:",
        document.extension,
    )
    print(
        "It contains the following annotation collection:",
        document.annotation_collections,
    )
    # add a new anncollection to the document, with a change of its version (sorted) and a comment
    document.add_annotation_collection(
        annot_col,
    )
    print("We added another annotation collection, a sorted version:", document)
    print("Sorted annotation collection:", document.annotation_collections[1])

    print(
        "\nReading Document 2 WITHOUT ann path given, but through subdirectory named txt:",
    )
    document = read_and_load_txt_file(
        txtpath=join("data", "demo", "txt", "myannfile2.txt"),
    )
    assert type(document) is Document
    print(document)
    print(document.annotation_collections)

    print(
        "\nalso, we can still make a Document instance if the ann file does not exist, the list of Annotation Collection will be empty though.",
    )
    document = read_and_load_txt_file(
        txtpath=join("data", "demo", "txt", "noannfile.txt"),
    )
    print(document)

    print(
        "\n\n###################################################### CLASS DocumentCollection ######################################################",
    )
    print(
        "\nRead all ann files from data/demo/both/ folder and builds a DocumentCollection object",
    )
    doc_collect = read_document_collection_from_folder(
        path=join("data", "demo", "both"),
    )
    assert type(doc_collect) is DocumentCollection
    print(doc_collect)
    print(
        "TXT/ANN COMPATIBILITY CHECKING... Is compatible:",
        doc_collect.check_ann_compatibility_with_txt(),
    )
    print("\nLet's get statistics !!")
    doc_collect.stats_annotation_types(verbose=True)
    doc_collect.stats_labels_given_annot_type(
        verbose=True,
        descendant_type=EntityAnnotation,
    )
    doc_collect.stats_entity_contents_given_label(
        verbose=True,
        label="DET",
    )

    print(
        "Finally, let's apply a change on the whole collection: let's keep only EntityAnnotation whose label is DET, and write the new ann files in the folder generated_ann_files.",
    )
    for doc in doc_collect.documents:
        for ann_coll in doc.annotation_collections:
            ann_coll.keep_specific_annotations(["DET"], EntityAnnotation)
            ann_coll.sort_annotations()
            ann_coll.renum()

    print("Writing the document collection somewhere (only ANN files)...")
    write_ann_files_in_folder(
        doc_collection=doc_collect,
        path=join(output_test, "generated_ann_files"),
    )
