import os

from bratly_eval import compare_folders


def main() -> None:
    path_data_test_eval = os.path.join(".", "data", "demo", "eval")
    path_output_test_eval = os.path.join(".", "dev_test", "eval")
    os.makedirs(path_output_test_eval, exist_ok=True)

    print("TEST1 with keep_specific_annotations")
    mc, csv, _ = compare_folders(os.path.join(path_data_test_eval, "test1", "auto"), os.path.join(path_data_test_eval, "test1", "ref"), keep_specific_annotations=["Place"])
    print(mc.get_global_statistics())
    print(csv)

    print("TEST2")
    mc, csv, _ = compare_folders(os.path.join(path_data_test_eval, "test2", "txt"), os.path.join(path_data_test_eval, "test2", "xxx"))
    print(mc.get_global_statistics())
    print(csv)

    print("TEST3 and writing eval reports")
    mc, csv, _ = compare_folders(
        os.path.join(path_data_test_eval, "test3", "medina"),
        os.path.join(path_data_test_eval, "test3", "tmp"),
        eval_folder=path_output_test_eval,
        muc_with_help=True,
    )
    print(mc.get_global_statistics())
