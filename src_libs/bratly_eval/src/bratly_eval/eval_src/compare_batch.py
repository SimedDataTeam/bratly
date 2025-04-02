from pathlib import Path
import pandas as pd
from .count_tokens import count_tokens_and_anns
from ..agreement_types import compare_folders


def contains_any(main_string, substrings):
    return any([substring in main_string for substring in substrings])


def extract_diffs(csv: str, labels: list[str], fields: tuple, batch: dict, write_files: bool=True):
    concepts = {}
    for line in [line for line in csv.split("\n") if contains_any(line, labels)]:
        split_line = line.split(",")
        concept = (split_line[fields[0]], split_line[fields[1]])
        if concept not in concepts:
            concepts[concept] = { 'n':0, 'files':[]}
        concepts[concept]['n'] += 1
        concepts[concept]['files'].append(split_line[0])

    # sort concept by frequency
    sorted_concepts = sorted(concepts.items(), key=lambda item: item[1]['n'], reverse=True)

    # rearrange items from ((label,semantic_tag),n) to (label,semantic_tag,n)
    if 'bratpath' in batch:
        bratpath = (Path(batch['bratpath']) / batch['corrected'] / concept[1]['files'][0]).with_suffix('') # http://vmld-01500.huge.ad.hcuge.ch:8001/index.xhtml#/benchmark
    else:
        bratpath = ""

    sorted_concepts = [
        [concept[0][0].replace('"', ""), concept[0][1], concept[1]['n'], "", str(bratpath)]
        for concept in sorted_concepts
    ]

    # fileout
    fileout = batch["datapathout"] / f"compare_{batch['name']}_{'_'.join(labels)}.xlsx"

    # create dataframe
    df = pd.DataFrame(sorted_concepts, columns=["label", "semantic_tag", "count", "SCT_multicode", "example"])

    # df.to_excel(fileout,index=False)

    writer = pd.ExcelWriter(fileout, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']

    # Iterate through the DataFrame and write URLs as hyperlinks
    for row_num, example in enumerate(df['example'], start=1):
        worksheet.write_url(row_num, 4, example, string="/".join(example.split("/")[-3:]))
    writer.close()


    return len(df)


def compare_batch(batch: dict, write_files: bool = True, max_n: int = -1):
    """ both folders must be flat"""
    if "datapath" not in batch:
        exit("no datapath in batch dict")
    if "datapathout" not in batch:
        batch["datapathout"] = batch["datapath"]
    batch["datapath"] = Path(batch["datapath"])
    batch["datapathout"] = Path(batch["datapathout"])

    print("===============\nCompare folders")
    mc, csv, df = compare_folders(
        str(batch["datapath"] / batch["auto"]),
        str(batch["datapath"] / batch["corrected"]),
        max_n=max_n,
    )

    stats = mc.get_global_statistics()
    # print(batch["corrected"], "vs", batch["auto"], f"{_stats['POSSIBLE']}:{_stats['F1']:.2f} ({_stats['PRECISION']:.2f})")
    # pprint(stats)

    print("=================================\nCount tokens and annonated tokens")
    n_doc, n_tokens, n_ann_tokens = count_tokens_and_anns(
        batch["datapath"] / batch["auto"],
        max_n=max_n,
    )

    CSVOUT = Path(batch["datapathout"]) / f"compare_{batch['name']}.csv"

    if write_files:
        # with CSVOUT.open("w", encoding="utf_8") as f:
        #     f.write(csv)
        # print(df)
        df.to_excel(CSVOUT.with_suffix(".xlsx"), index=False)

    # create files
    n_unique_missing = extract_diffs(csv, ["MISSING"], (13, 9), batch, write_files=write_files)
    n_unique_partial = extract_diffs(csv, ["PARTIAL"], (13, 9), batch, write_files=write_files)
    n_unique_spurious = extract_diffs(csv, ["SPURIOUS"], (7, 3), batch, write_files=write_files)

    print("docs:", n_doc, "\ntokens", n_tokens, "\nannotations", n_ann_tokens)
    stat_list = [n_doc, n_tokens, n_ann_tokens,
                100 * n_ann_tokens / n_tokens,
                -1,                          # placeholder
                100 * stats["OVERGENERATION"],
                stats["SPURIOUS"],
                100 * stats["UNDERGENERATION"],
                stats["MISSING"],
                100 * stats["RECALL"],
                100 * stats["PRECISION"],
                100 * stats["F1"],
                n_unique_spurious,
                -1,                          # placeholder
                n_unique_missing,
                n_unique_partial
            ]
    print(";".join(f"{num:.2f}" if isinstance(num,float) else str(num) for num in stat_list))
    print("ndocs,ntoks,nanns,nanns/ntoks,-1,overgen,spurious,undergen,missing,recall,precision,f1,unique_spurious,-1,unique_missing,unique_partial")
