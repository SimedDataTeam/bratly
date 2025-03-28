import os
from bratly_eval import create_union_gold_candidate_sets, compare_folders, MucTable


def main() -> None:
    path_data_test_eval = os.path.join('.', 'data', 'demo', 'eval')
    path_output_test_eval = os.path.join('.', 'dev_test', 'eval')
    os.makedirs(path_output_test_eval, exist_ok=True)

    print("TEST1-keep_specific_annotations ")
    mc, csv, df_agreement = compare_folders(os.path.join(path_data_test_eval, 'test1', 'auto'), os.path.join(path_data_test_eval, 'test1', 'ref'), keep_specific_annotations=["Place"])

    print("TEST_UNION")
    create_union_gold_candidate_sets(
        path_doc_col_gs=os.path.join(path_data_test_eval, "test4_drugs", "batch1_16_v2"),
        path_doc_col_auto=os.path.join(path_data_test_eval, "test4_drugs", "sub_and_class"),
        path_output_newgold_folder=os.path.join(path_data_test_eval, "test4_drugs", "union"),
        copy_txt_files=True,
    )
    print(mc.get_global_statistics())
    print(csv)

    print("TEST2")
    mc, csv, df_agreement = compare_folders(os.path.join(path_data_test_eval, 'test2', 'txt'), os.path.join(path_data_test_eval, 'test2', 'xxx'))
    print(mc.get_global_statistics())
    print(csv)

    print("TEST3")
    mc, csv, df_agreement = compare_folders(os.path.join(path_data_test_eval, 'test3', 'medina'), os.path.join(path_data_test_eval, 'test3', 'tmp'))
    print(mc.get_global_statistics())
    print(
        "Precision range",
        min([mt.get_statistics()["PRECISION"] for mt in mc.muc_tables]),
        max([mt.get_statistics()["PRECISION"] for mt in mc.muc_tables]),
    )
    print(
        "Precisions", sorted(mt.get_statistics()["PRECISION"] for mt in mc.muc_tables)
    )
    print(
        "Recall range",
        min([mt.get_statistics()["RECALL"] for mt in mc.muc_tables]),
        max([mt.get_statistics()["RECALL"] for mt in mc.muc_tables]),
    )
    print("Recalls", sorted(mt.get_statistics()["RECALL"] for mt in mc.muc_tables))

    print("TEST4")
    mc, csv, df_agreement = compare_folders(
        os.path.join(path_data_test_eval, 'test4_drugs', 'batch1_16_v2'), os.path.join(path_data_test_eval, 'test4_drugs', 'sub_and_class')
    )
    print(mc.get_global_statistics(with_help=True))
    print(
        "Precision range",
        min([mt.get_statistics()["PRECISION"] for mt in mc.muc_tables]),
        max([mt.get_statistics()["PRECISION"] for mt in mc.muc_tables]),
    )
    print(
        "Precisions", sorted(mt.get_statistics()["PRECISION"] for mt in mc.muc_tables)
    )
    print(
        "Recall range",
        min([mt.get_statistics()["RECALL"] for mt in mc.muc_tables]),
        max([mt.get_statistics()["RECALL"] for mt in mc.muc_tables]),
    )
    print("Recalls", sorted(mt.get_statistics()["RECALL"] for mt in mc.muc_tables))

    print("TEST4 writing eval file")
    mc, csv, df_agreement = compare_folders(
        os.path.join(path_data_test_eval, 'test4_drugs', 'batch1_16_v2'),
        os.path.join(path_data_test_eval, 'test4_drugs', 'sub_and_class'),
        eval_folder=path_output_test_eval,
        muc_with_help=True
    )
