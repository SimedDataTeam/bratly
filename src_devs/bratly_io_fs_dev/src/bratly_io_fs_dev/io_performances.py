import time
from pathlib import Path

from bratly.collection_types import DocumentCollection
from bratly.io import read_document_collection_from_folder, write_ann_files_in_folder


def main(path_datasets: str = "./data/bratly_datasets/"):
    """
    Process each folder in the given path and measure the time taken for each.

    Args:
        path_datasets: Path containing folders to process

    Returns:
        Dictionary mapping folder names to processing times (in seconds)

    """
    results = {}

    # Convert to Path object for easier handling
    base_path = Path(path_datasets)

    # Check if path exists
    if not base_path.exists():
        print(f"Error: Path '{path_datasets}' does not exist")
        return results

    # Get all subdirectories
    subdirectories = [d for d in base_path.iterdir() if d.is_dir()]

    if not subdirectories:
        print(f"No folders found in '{path_datasets}'")
        return results

    # Process each folder and measure time
    for folder in subdirectories:
        folder_results = {}
        print(f"Working with {folder.name}")
        start_time = time.time()
        mydc = read_document_collection_from_folder(str(folder))
        assert type(mydc) is DocumentCollection
        end_time = time.time()

        elapsed_time = end_time - start_time
        folder_results["read_time"] = elapsed_time
        nbdocs = len(mydc.documents)
        print(f"DocumentCollection '{folder.name}' read in {elapsed_time:.4f} seconds - it contains {nbdocs} annotated files whose statistics are:")
        annot_stats = mydc.stats_annotation_types()
        print(annot_stats)

        # Create output folder
        output_folder_name = f"{folder.name}_output"
        output_folder_path = folder.parent / output_folder_name

        # Create the output folder if it doesn't exist
        output_folder_path.mkdir(exist_ok=True)

        # Measure time for writing annotation files
        start_time = time.time()
        write_ann_files_in_folder(mydc, str(output_folder_path))
        end_time = time.time()

        write_time = end_time - start_time
        folder_results["write_time"] = write_time
        print(f"Output for '{folder.name}' written in {write_time:.4f} seconds")

        # Store results for this folder
        results[folder.name] = folder_results

    if results:
        print("\nSummary of processing times:")
        print("-" * 60)
        print(f"{'Folder':<30} {'Read Time (s)':<15} {'Write Time (s)':<15} {'Total (s)':<15}")
        print("-" * 60)
        for folder, times in results.items():
            total_time = times["read_time"] + times["write_time"]
            print(f"{folder:<30} {times['read_time']:.4f}{'':>8} {times['write_time']:.4f}{'':>8} {total_time:.4f}{'':>8}")

    return results
