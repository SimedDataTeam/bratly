from pathlib import Path
from os.path import join
import shutil
from bratly import AnnotationCollection, DocumentCollection


def write_ann_file(annotations: AnnotationCollection, path: str) -> None:
    """Writes the content of a list of annotations to the file specified in path"""
    ann_str = ""
    if hasattr(annotations, 'annotations'):
        for annotation in annotations.annotations:
            ann_str += f"{str(annotation)}\n"

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    feed = open(path, "w", encoding="utf_8")
    feed.write(ann_str)
    feed.close()


def write_ann_files_in_folder(doc_collection: DocumentCollection, path: str) -> None:
    """Writes the ann content of a document collection to the folder specified in path"""
    for doc in doc_collection.documents:
        ann_collections = doc.annotation_collections
        if len(ann_collections) == 0:
            continue
        elif len(ann_collections) > 1:
            raise NotImplementedError(
                "Writing DocumentCollection with at least one Document object having multiple AnnotationCollection objects is not implemented yet."
            )
        else:
            # write ann file
            write_ann_file(
                annotations=ann_collections[0],
                path=join(path, doc.filename_without_ext + ".ann"),
            )


def copy_txt_from_collection_to_another_path(
    doc_collection: DocumentCollection, path_to_folder: str
) -> None:
    """Copies the txt files from the current collection to another, useful when you're creating a new collection from this one"""
    for doc in doc_collection.documents:
        srcpath = doc.fullpath
        dstpath = join(path_to_folder, doc.filename_without_ext + ".txt")
        shutil.copy(srcpath, dstpath)
