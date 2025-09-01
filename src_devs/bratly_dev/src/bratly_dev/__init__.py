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
    ann1 = EntityAnnotation(id="T1", label="LabelX", fragments=[Fragment(start=1, end=3)], content="xx")
    ann2 = EntityAnnotation(id="2", label="LabelY", fragments=[Fragment(start=3, end=5)], content="yy")
    ann_note1 = NoteAnnotation(
        id="#1",
        label="AnnotatorNotes",
        component=ann2,
        value="This is a note we give, un certain T2 parlant de yy",
    )
    print("- Annotation 1:", ann1)
    print("- Annotation 2:", ann2)

    # print("If we don't instantiate the id properly, an exception is raised:")
    # invalid_annotation = EntityAnnotation("S1", "LabelY", [Fragment(3, 5)], "yy")

    print(
        "\n\n########################################## ANNOTATION COLLECTION: CREATION AND ADDING ANNOTATIONS ###########################################################",
    )
    # create an empty annotation collection
    anns = AnnotationCollection(annotations=[])
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
    ann2_diffid = EntityAnnotation(id="T3", label="LabelY", fragments=[Fragment(start=3, end=5)], content="yy")
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
    ann3 = EntityAnnotation(id="T1", label="LabelX", fragments=[Fragment(start=1, end=3)], content="xx")
    ann4 = EntityAnnotation(id="2", label="LabelY", fragments=[Fragment(start=8, end=14)], content="chemin")
    ann_note2 = NoteAnnotation(
        id="#1",
        label="AnnotatorNotes",
        value="This is a note we give, un certain T2 parlant de chemin",
        component=ann4,
    )
    anns2 = AnnotationCollection(annotations=[ann3, ann4, ann_note2])
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
    ann3 = EntityAnnotation(id="3", label="LabelY", fragments=[Fragment(start=7, end=9)], content="yy")
    ann4 = EntityAnnotation(id="4", label="LabelY", fragments=[Fragment(start=11, end=12)], content="y")
    anns.extend_annotation([ann3, ann4])
    print("-- Annotation 3:", ann3)
    print("-- Annotation 4:", ann4)
    print(anns.get_annotations())
    print("- Giving statistics about the collection:")
    anns.stats_annotation_types(verbose=True)
    print("- Giving statistics about the labels among entities:")
    anns.stats_labels_given_annot_type(
        verbose=True,
        descendant_type=EntityAnnotation,
    )
    print(
        "- Giving statistics about the contents from the label LabelY among entities:",
    )
    anns.stats_entity_contents_given_label(
        label="LabelY",
        verbose=True,
    )

    print(
        "\n\n########################################## ANNOTATION COLLECTION: REMOVE CONTAINED ANNOTATIONS ###########################################################",
    )
    print(
        "- Suppose that we have another annotation, Annotation5, which is contained in another annotation, let's say Annotation 3:",
    )
    ann5 = EntityAnnotation(id="5", label="LabelY", fragments=[Fragment(start=7, end=8)], content="y")
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
    ann3 = NoteAnnotation(id="#1", label="AnnotatorNotes", value="This is a note we give", component=ann2)
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
