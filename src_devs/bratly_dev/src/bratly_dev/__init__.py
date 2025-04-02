import os

from bratly import (
    AnnotationCollection,
    EntityAnnotation,
    Fragment,
    NoteAnnotation,
)


def main():
    print(
        "########################################## ENTITY ANNOTATION ###########################################################",
    )
    # create two entity annotations (with the ID being a str written with or without the EntityAnnotation mark T)
    ann1 = EntityAnnotation("T1", "LabelX", [Fragment(1, 3)], "xx")
    ann2 = EntityAnnotation("2", "LabelY", [Fragment(3, 5)], "yy")
    ann_note1 = NoteAnnotation(
        "#1",
        "AnnotatorNotes",
        "This is a note we give, un certain T2 parlant de yy",
        ann2,
    )
    print("- Annotation 1:", ann1)
    print("- Annotation 2:", ann2)

    # print("If we don't instantiate the id properly, an exception is raised:")
    # invalid_annotation = EntityAnnotation("S1", "LabelY", [Fragment(3, 5)], "yy")

    print(
        "\n\n########################################## ANNOTATION COLLECTION: CREATION AND ADDING ANNOTATIONS ###########################################################",
    )
    # create an empty annotation collection
    anns = AnnotationCollection([])
    anns.add_annotation(ann2)
    print(
        "- Added Annotation 2 in collection through add_annotation method, the collection:",
    )
    print(anns)
    print(anns.get_annotations())
    print(
        "- Added both annotations in collection through extend_annotation method, the collection:",
    )
    anns.extend_annotation([ann1, ann2])
    print(anns)
    print(anns.get_annotations())
    print(
        "- Testing the ability of the classes to be immutable, an Exception should be found here:",
    )
    try:
        anns.annotations += [ann1, ann2]
        print(anns)
    except Exception as exc:
        print("Error found:", exc)

    print(
        "\n\n########################################## ANNOTATION COLLECTION: REMOVING DUPLICATES AND SORTING ANNOTATIONS ###########################################################",
    )
    ann2_diffid = EntityAnnotation("T3", "LabelY", [Fragment(3, 5)], "yy")
    anns.add_annotation(ann2_diffid)
    print("Current annotations:")
    print(anns)
    print(anns.get_annotations())
    print("- Removing the duplicates, the collection:")
    anns.remove_duplicates()
    print(anns)
    print(anns.get_annotations())
    print("- Sorting the annotations, the collection:")
    anns.sort_annotations()
    print(anns)
    print(anns.get_annotations())

    print(
        "\n\n########################################## ANNOTATION COLLECTION: COMBINING ANNOTATIONS ###########################################################",
    )
    ann3 = EntityAnnotation("T1", "LabelX", [Fragment(1, 3)], "xx")
    ann4 = EntityAnnotation("2", "LabelY", [Fragment(8, 14)], "chemin")
    ann_note2 = NoteAnnotation(
        "#1",
        "AnnotatorNotes",
        "This is a note we give, un certain T2 parlant de chemin",
        ann4,
    )
    anns2 = AnnotationCollection([ann3, ann4, ann_note2])
    anns.add_annotation(ann_note1)
    print("- Trying the function combining these two AnnotationCollection:")
    print(anns.get_annotations())
    print(anns2.get_annotations())
    print("- Combined collection:")
    anns.combine(anns2, with_renum=True)
    print(anns.get_annotations())

    print(
        "\n\n########################################## ANNOTATION COLLECTION: STATISTICS FUNCTIONS ###########################################################",
    )
    print("- Added two more annotations:")
    ann3 = EntityAnnotation("3", "LabelY", [Fragment(7, 9)], "yy")
    ann4 = EntityAnnotation("4", "LabelY", [Fragment(11, 12)], "y")
    anns.extend_annotation([ann3, ann4])
    print("-- Annotation 3:", ann3)
    print("-- Annotation 4:", ann4)
    print(anns.get_annotations())
    print("- Giving statistics about the collection:")
    mon_dico = anns.stats_annotation_types(verbose=True)
    print("- Giving statistics about the labels among entities:")
    mon_dico = anns.stats_labels_given_annot_type(
        verbose=True,
        descendant_type=EntityAnnotation,
    )
    print(
        "- Giving statistics about the contents from the label LabelY among entities:",
    )
    mon_dico = anns.stats_entity_contents_given_label(
        label="LabelY",
        verbose=True,
    )

    print(
        "\n\n########################################## ANNOTATION COLLECTION: REMOVE CONTAINED ANNOTATIONS ###########################################################",
    )
    print(
        "- Suppose that we have another annotation, Annotation5, which is contained in another annotation, let's say Annotation 3:",
    )
    ann5 = EntityAnnotation("5", "LabelY", [Fragment(7, 8)], "y")
    anns.add_annotation(ann5)
    print("-- Annotation 5:", ann5)
    print("-- Annotation 3:", ann3)
    print("The collection before removal of contained annotations:", anns)
    anns.remove_contained_annotations()
    print("The collection after removal of contained annotations:", anns)

    print(
        "\n\n########################################## ANNOTATION COLLECTION: FILTERING BY ANNOTATION TYPE AND LABEL ###########################################################",
    )
    print("- Keeping the EntityAnnotation whose label is LabelY, the collection:")
    anns.keep_specific_annotations(["LabelY"], EntityAnnotation)
    print(anns.get_annotations())

    print(
        "\n\n########################################## ANNOTATION COLLECTION: GETTERS ###########################################################",
    )
    ann3 = NoteAnnotation("#1", "AnnotatorNotes", "This is a note we give", ann2)
    anns.remove_duplicates()
    anns.add_annotation(ann3)
    print("- We remove duplicates, and then add a NoteAnnotation. The collection:")
    print(anns.get_annotations())
    print("- We get only the EntityAnnotation instances, the entities:")
    print(anns.get_annotations(EntityAnnotation))
    print("- We get only the NoteAnnotation instances, the notes:")
    print(anns.get_annotations(NoteAnnotation))

    print(
        "\n\n########################################## ANNOTATION COLLECTION: WE SAVE THE WHOLE ANNOTATION COLLECTION IN JSON ###########################################################",
    )
    path_output = os.path.join(".", "dev_test")
    os.makedirs(path_output, exist_ok=True)
    json_path = os.path.join(path_output, "my_json_file.json")
    anns.to_json(path_json_file=json_path)
    # see bratly_io_fs_dev for use of Document and DocumentCollection
