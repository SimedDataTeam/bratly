import os

from bratly_eval import MucTable, compare_folders, create_union_gold_candidate_sets


def main() -> None:
    path_data_test_eval = os.path.join(".", "data", "demo", "eval")
    os.makedirs(path_data_test_eval, exist_ok=True)

    print("TEST2")
    mc, csv, df_agreement = compare_folders(os.path.join(path_data_test_eval, "test2", "txt"), os.path.join(path_data_test_eval, "test2", "xxx"))
    print(mc.get_global_statistics())
    print(csv)

    print("TEST3")
    mc, csv, df_agreement = compare_folders(os.path.join(path_data_test_eval, "test3", "medina"), os.path.join(path_data_test_eval, "test3", "tmp"))
    print(mc.get_global_statistics())
    print(
        "Precision range",
        min([mt.get_statistics()["PRECISION"] for mt in mc.muc_tables]),
        max([mt.get_statistics()["PRECISION"] for mt in mc.muc_tables]),
    )
    print(
        "Precisions",
        sorted(mt.get_statistics()["PRECISION"] for mt in mc.muc_tables),
    )
    print(
        "Recall range",
        min([mt.get_statistics()["RECALL"] for mt in mc.muc_tables]),
        max([mt.get_statistics()["RECALL"] for mt in mc.muc_tables]),
    )
    print("Recalls", sorted(mt.get_statistics()["RECALL"] for mt in mc.muc_tables))
