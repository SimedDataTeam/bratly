from bratly_io_fs import read_document_collection_from_folder, write_ann_files_in_folder
from bratly import (
    DocumentCollection,
    EntityAnnotation,
)


def duplicate_document_collection_with_specific_annotations(
    doccol_input_path: str,
    doccol_output_path: str,
    labels_to_keep: list[str],
    involved_annot_type=EntityAnnotation,
) -> DocumentCollection:
    """ Copy an existing document collection, while keeping only a specific subset of annotations given their labels """
    # read the doccollection
    doccol: DocumentCollection = read_document_collection_from_folder(
        path=doccol_input_path,
        no_duplicates_ann=False,
        sort_ann=False,
        renumerotize_ann=False,
        grammar_check_ann=True,
    )
    # keep the expected annotations
    for doc in doccol.documents:
        doc.annotation_collections[0].keep_specific_annotations(
            labels=labels_to_keep, annot_type=involved_annot_type
        )
        doc.annotation_collections[0].remove_orphan_notes()
        doc.annotation_collections[0].sort_annotations()
        doc.annotation_collections[0].renum()
    # saves the new collection
    write_ann_files_in_folder(doccol, doccol_output_path)
    return doccol
