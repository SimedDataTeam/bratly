from collections import Counter
from typing import Any, ClassVar, Literal

import numpy as np
from bratly import EntityAnnotation, Fragment
from pydantic import BaseModel


class FragmentAgreement(BaseModel):
    """
    Object describing the similarity between two fragments (gold_frag, parallel_frag).
    Flag is correct if ends and starts are the same,
    partial if there is a non-empty intersection between the fragments, but either start or end or both differ.
    For partial 8 cases exist (see readme)
    Flag is spurious if there is no corresponding gold for parallel,
    missing if there is no corresponding parallel for gold.
    """

    gold_frag: Fragment
    parallel_frag: Fragment
    flag: int  # 0: correct, #1-8: partial 1-8, #9: spurious, #10: missing

    def __init__(
        self,
        gold_frag: Fragment | None = None,
        parallel_frag: Fragment | None = None,
    ) -> None:
        """
        Init: Either gold or parallel fragment have to be specified"""
        object.__setattr__(self, "parallel_frag", parallel_frag)
        object.__setattr__(self, "gold_frag", gold_frag)
        if not parallel_frag and not gold_frag:
            raise NotImplementedError
        if not gold_frag:
            object.__setattr__(self, "flag", 9)
        elif not parallel_frag:
            object.__setattr__(self, "flag", 10)
        else:
            if self.parallel_frag.start < self.gold_frag.start:
                flag = 6
            elif self.parallel_frag.start == self.gold_frag.start:
                flag = 0
            else:
                flag = 3
            if self.parallel_frag.end < self.gold_frag.end:
                flag += 1
            elif self.parallel_frag.end > self.gold_frag.end:
                flag += 2
            object.__setattr__(self, "flag", flag)

    def tag_from_flag(self) -> str:
        """
        Returns the str name of the flag stored as an integer"""
        if self.flag == 0:
            return "correct"
        if self.flag < 9:
            return f"partial{self.flag}"
        if self.flag == 9:
            return "spurious"
        return "missing"

    def contains(self, other: "FragmentAgreement") -> bool:
        """Returns whether the the scope of current agreement is larger then that of the other."""
        return (max(self.gold_frag.start, self.parallel_frag.start) <= max(other.gold_frag.start, other.parallel_frag.start)) and (
            min(self.gold_frag.end, self.parallel_frag.end) >= min(other.gold_frag.end, other.parallel_frag.end)
        )

    def is_distinct(self, others: list["FragmentAgreement"]) -> bool:
        """Returns whether it is distinct from any other agreements in the list."""
        return all(not o.contains(self) for o in others)

    def __str__(self) -> str:
        """For printing: returns the flag of the agreement and the two fragmentes compared"""
        return f"{self.tag_from_flag()}: {self.parallel_frag},{self.gold_frag}"

    def __repr__(self) -> str:
        return str(self)

    def __lt__(self, other: Any) -> bool:
        """
        Returns whether the scope of the current FragmentAgreement is occuring earlier than that of the others.
        The scope occurs earlier if it starts earlier, or - in case of same start - it ends earlier.
        For missing and spurious agreements, the scope is defined here as the scope of the missing or spurious fragment.
        """
        if isinstance(other, "FragmentAgreement"):
            comparison_vector = [-1, -1, -1, -1]
            if self.parallel_frag and self.gold_frag:
                comparison_vector[0:2] = [
                    max(self.parallel_frag.start, self.gold_frag.start),
                    min(self.parallel_frag.end, self.gold_frag.end),
                ]
            elif self.gold_frag:
                comparison_vector[0:2] = [self.gold_frag.start, self.gold_frag.end]
            elif self.parallel_frag:
                comparison_vector[0:2] = [
                    self.parallel_frag.start,
                    self.parallel_frag.end,
                ]
            else:
                raise NotImplementedError
            if other.parallel_frag and other.gold_frag:
                comparison_vector[2:4] = [
                    max(other.parallel_frag.start, other.gold_frag.start),
                    min(other.parallel_frag.end, other.gold_frag.end),
                ]
            elif other.gold_frag:
                comparison_vector[2:4] = [other.gold_frag.start, other.gold_frag.end]
            elif other.parallel_frag:
                comparison_vector[2:4] = [
                    other.parallel_frag.start,
                    other.parallel_frag.end,
                ]
            else:
                raise NotImplementedError
            return comparison_vector[0:2] < comparison_vector[2:4]
        return False


class Agreement(BaseModel):
    """
    Object describing the similarity between two entity annotations (gold, parallel).
    Flag is correct if ends and starts are the same and the two annotations have the same type;
    Incorrect if ends and starts are the same but the types are different;
    Partial if there is a non-empty intersection between the fragments, but either start or end or both differ and the type is the same,
    Related if the match is partial but the types are different.
    There are 2 cases for partial and for related flags, if there is partial/correct match between all fragments or when only between some of them.
    Flag is spurious if there is no corresponding gold for parallel,
    missing if there is no corresponding parallel for gold.
    """

    gold: EntityAnnotation
    parallel: EntityAnnotation
    fragment_agreements: list[FragmentAgreement]
    flag: int  # 0: correct, 1: incorrect, 2: missing, 3: spurious
    # 4: partial (all fragments), 5: partial (some fragments)
    # 6: related (all fragments), 7: related (some fragments)
    coverage: tuple[int, int]

    @staticmethod
    def merge_inclusive(fr1: Fragment, fr2: Fragment) -> Fragment:
        """Helper function returning the maximum scope (union) of two intersecting fragments"""
        if not fr1:
            return fr2
        if not fr2:
            return fr1
        return Fragment(min(fr1.start, fr2.start), max(fr1.end, fr2.end))

    @staticmethod
    def merge_exclusive(fr1: Fragment, fr2: Fragment) -> Fragment | None:
        """Helper function returning the minimum scope (intersection) of two intersecting fragments"""
        if not fr1 or not fr2 or fr1.end <= fr2.start or fr2.end <= fr1.start:
            return None
        return Fragment(max(fr1.start, fr2.start), min(fr1.end, fr2.end))

    @staticmethod
    def union(fragments: list[FragmentAgreement]) -> list[Fragment]:
        """Helper function returning the union of FragmentAgreements (i.e. eliminating duplicates)"""
        tmp = [
            Agreement.merge_inclusive(
                fragments[0].gold_frag,
                fragments[0].parallel_frag,
            ),
        ]
        j = 0
        for i, f in enumerate(sorted(fragments)[1:]):
            tmp2 = Agreement.merge_inclusive(
                fragments[i].gold_frag,
                fragments[i].parallel_frag,
            )
            if tmp[j] and tmp[j].end >= tmp2.start:
                tmp[j] = Fragment(tmp[j].start, tmp2.end)
            else:
                tmp.append([])
                j += 1
        return np.sum([f.end - f.start for f in tmp if f])

    @staticmethod
    def intersect(fragments: list[FragmentAgreement]) -> list[Fragment]:
        """Helper function returning the intersection of FragmentAgreements (contained by all of them)"""
        tmp = []
        for i, f in enumerate(sorted(fragments)[:-1]):
            tmp2 = Agreement.merge_exclusive(f, fragments[i + 1])
            if tmp2:
                tmp.append(tmp2)
        if tmp:
            return Agreement.union(tmp)
        return []

    def __init__(
        self,
        fragment_agreements: list[FragmentAgreement],
        parallel: EntityAnnotation | None,
        gold: EntityAnnotation | None,
    ) -> None:
        if len(fragment_agreements) < 1:
            raise NotImplementedError
        object.__setattr__(self, "gold", gold)
        object.__setattr__(self, "parallel", parallel)
        object.__setattr__(self, "fragment_agreements", fragment_agreements)
        object.__setattr__(
            self,
            "coverage",
            (
                Agreement.intersect(fragment_agreements),
                Agreement.union(fragment_agreements),
            ),
        )
        if all(fa.flag == 0 for fa in fragment_agreements):
            if len(fragment_agreements) == len(self.gold.fragments):
                # print(fragment_agreements,self.gold,self.parallel)
                if self.gold.label == self.parallel.label:
                    object.__setattr__(self, "flag", 0)
                else:
                    object.__setattr__(self, "flag", 1)
            elif self.gold.label == self.parallel.label:
                object.__setattr__(self, "flag", 5)
            else:
                object.__setattr__(self, "flag", 7)
        elif all(fa.flag == 9 for fa in fragment_agreements):
            object.__setattr__(self, "flag", 3)
        elif all(fa.flag == 10 for fa in fragment_agreements):
            object.__setattr__(self, "flag", 2)
        elif len(fragment_agreements) == len(self.gold.fragments):
            if not fragment_agreements[0].gold_frag or not fragment_agreements[0].parallel_frag:
                raise NotImplementedError
            if all(fa.flag < 9 and fa.flag > 0 for fa in fragment_agreements):
                if self.gold.label == self.parallel.label:
                    object.__setattr__(self, "flag", 4)
                else:
                    object.__setattr__(self, "flag", 6)
            elif self.gold.label == self.parallel.label:
                object.__setattr__(self, "flag", 5)
            else:
                object.__setattr__(self, "flag", 7)
        elif any(fa.flag < 9 and fa.flag > 0 for fa in fragment_agreements):
            if not fragment_agreements[0].gold_frag or not fragment_agreements[0].parallel_frag:
                raise NotImplementedError
            if self.gold.label == self.parallel.label:
                object.__setattr__(self, "flag", 5)
            else:
                object.__setattr__(self, "flag", 7)
        else:
            print(fragment_agreements, gold, parallel)
            raise NotImplementedError

    def flag_in_str(self) -> str:
        """Helper function converting the flag to the corresponding string"""
        match self.flag:
            case 0:
                return "CORRECT"
            case 1:
                return "INCORRECT"
            case 2:
                return "MISSING"
            case 3:
                return "SPURIOUS"
            case 4:
                return "PARTIAL_A"
            case 5:
                return "PARTIAL_S"
            case 6:
                return "RELATED_A"
            case 7:
                return "RELATED_S"
            case _:
                return "UNKNOWN"

    @staticmethod
    def annotation_to_csv(ann: EntityAnnotation, filename=""):
        """Converts one line of annotation to CSV format (part of one line)"""
        if ann:
            fr_str = ";".join([str(a) for a in ann.fragments])
            return f'{ann.id},{ann.label},{ann.get_start()},{ann.get_end()},{fr_str},"{ann.content}"'
        return ",,,,,"

    def to_csv(self, filename: str | None = None) -> str:
        """Converts an agreement to one line of CSV file"""
        flag_names = ["c", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "s", "m"]
        interval_match = ";".join(
            [flag_names[fa.flag] for fa in self.fragment_agreements],
        )
        if filename:
            return f"{filename},{self.flag_in_str()},{self.annotation_to_csv(self.parallel)},{self.annotation_to_csv(self.gold)},{interval_match}\n"
        return f"{self.flag_in_str()},{self.annotation_to_csv(self.parallel)},{self.annotation_to_csv(self.gold)},{interval_match}\n"

    def __str__(self) -> str:
        return f"{self.flag_in_str()}\t{self.parallel}\t{self.gold}"


class MucTable(BaseModel):
    """
    Data structure object reflecting the parameters of MUC-5 scoring scheme.
    Extended with some additional parameters
    """

    agreements: list[Agreement]
    correct: int
    incorrect: int
    partial_A: int
    partial_S: int
    related_A: int
    related_S: int
    missing: int
    spurious: int
    # token / letter coverage of the annotations
    partial_match_coverage: tuple[int, int]

    RELAXED_COMPARISON: ClassVar[int] = 1
    STRICT_COMPARISON: ClassVar[int] = 2
    BORDER_COMPARISON: ClassVar[int] = 3

    @staticmethod
    def safe_divide(a: int, b: int)-> float | Literal[0]:  # If divident 0, return 0
        return 0 if b == 0 else a / b

    def __init__(self, agreements: list[Agreement]) -> None:
        object.__setattr__(self, "agreements", agreements)
        c = Counter([a.flag for a in self.agreements])
        # print("c", c, c[0], c[6])
        object.__setattr__(self, "correct", c[0])
        object.__setattr__(self, "incorrect", c[1])
        object.__setattr__(self, "missing", c[2])
        object.__setattr__(self, "spurious", c[3])
        object.__setattr__(self, "partial_A", c[4])
        object.__setattr__(self, "partial_S", c[5])
        object.__setattr__(self, "related_A", c[6])
        object.__setattr__(self, "related_S", c[7])
        object.__setattr__(
            self,
            "partial_match_coverage",
            (
                np.sum([a.coverage[0] for a in agreements]),
                np.sum([a.coverage[1] for a in agreements]),
            ),
        )

    def get_statistics(
        self,
        comparison_type: int = RELAXED_COMPARISON,
    ) -> dict[str, float]:
        """
        Returns the most importantant statistics values for the comparison
        as a dictionary.
        """
        stats = {}
        stats["CORRECT"] = np.sum(self.correct)
        stats["INCORRECT"] = np.sum(self.incorrect)
        stats["PARTIAL_ALLFRAGMENTS"] = np.sum(self.partial_A)
        stats["PARTIAL_SOMEFRAGMENTS"] = np.sum(self.partial_S)
        stats["PARTIAL"] = stats["PARTIAL_ALLFRAGMENTS"] + stats["PARTIAL_SOMEFRAGMENTS"]
        stats["RELATED_ALLFRAGMENTS"] = np.sum(self.related_A)
        stats["RELATED_SOMEFRAGMENTS"] = np.sum(self.related_S)
        stats["RELATED"] = stats["RELATED_ALLFRAGMENTS"] + stats["RELATED_SOMEFRAGMENTS"]
        stats["MISSING"] = np.sum(self.missing)
        stats["SPURIOUS"] = np.sum(self.spurious)
        stats["POSSIBLE"] = stats["CORRECT"] + stats["INCORRECT"] + stats["MISSING"] + stats["PARTIAL"]
        stats["ACTUAL"] = stats["CORRECT"] + stats["INCORRECT"] + stats["SPURIOUS"] + stats["PARTIAL"]
        stats["BORDER CORRECT"] = stats["CORRECT"] + stats["INCORRECT"]
        stats["INCORRECT_BORDER"] = stats["PARTIAL"] + stats["SPURIOUS"]
        stats["UNDERGENERATION"] = MucTable.safe_divide(
            stats["MISSING"],
            stats["POSSIBLE"],
        )
        stats["OVERGENERATION"] = MucTable.safe_divide(
            stats["SPURIOUS"],
            stats["ACTUAL"],
        )
        match comparison_type:
            case MucTable.RELAXED_COMPARISON:
                stats["RECALL"] = MucTable.safe_divide(
                    stats["CORRECT"] + stats["PARTIAL"] + stats["INCORRECT"],
                    stats["POSSIBLE"],
                )
                stats["PRECISION"] = MucTable.safe_divide(
                    stats["CORRECT"] + stats["PARTIAL"] + stats["INCORRECT"],
                    stats["ACTUAL"],
                )
                stats["SUBSTITUTION"] = MucTable.safe_divide(
                    stats["INCORRECT"],
                    stats["CORRECT"] + stats["PARTIAL"] + stats["INCORRECT"],
                )
            case MucTable.STRICT_COMPARISON:
                stats["RECALL"] = MucTable.safe_divide(
                    stats["CORRECT"],
                    stats["POSSIBLE"],
                )
                stats["PRECISION"] = MucTable.safe_divide(
                    stats["CORRECT"],
                    stats["ACTUAL"],
                )
                stats["SUBSTITUTION"] = MucTable.safe_divide(
                    stats["INCORRECT"] + stats["PARTIAL"],
                    stats["CORRECT"] + stats["PARTIAL"] + stats["INCORRECT"],
                )
            case MucTable.BORDER_COMPARISON:
                stats["RECALL"] = MucTable.safe_divide(
                    stats["BORDER CORRECT"],
                    stats["POSSIBLE"],
                )
                stats["PRECISION"] = MucTable.safe_divide(
                    stats["BORDER CORRECT"],
                    stats["ACTUAL"],
                )
                stats["SUBSTITUTION"] = MucTable.safe_divide(
                    stats["INCORRECT_BORDER"],
                    stats["BORDER CORRECT"] + stats["INCORRECT_BORDER"],
                )
        if stats["PRECISION"] + stats["RECALL"] != 0:
            stats["F1"] = (2 * stats["PRECISION"] * stats["RECALL"])/(stats["PRECISION"] + stats["RECALL"])
        else:
            stats["F1"] = 0.0
        return stats


class MucCollection(BaseModel):
    """
    Class describing the comparison between several pairs of files.
    A collection of MucTables
    """

    muc_tables: list[MucTable]
    source_ids: list[str]
    corrects: list[int]
    incorrects: list[int]
    partial_As: list[int]
    partial_Ss: list[int]
    related_As: list[int]
    related_Ss: list[int]
    missings: list[int]
    spuriouses: list[int]

    def __init__(
        self,
        muc_tables: list[MucTable],
        source_ids: list[str] | None = None,
    ) -> None:
        object.__setattr__(self, "muc_tables", muc_tables)
        if not source_ids:
            object.__setattr__(self, "source_ids", ["" for _ in range(len(muc_tables))])
        object.__setattr__(self, "corrects", [mt.correct for mt in self.muc_tables])
        object.__setattr__(self, "incorrects", [mt.incorrect for mt in self.muc_tables])
        object.__setattr__(self, "partial_As", [mt.partial_A for mt in self.muc_tables])
        object.__setattr__(self, "partial_Ss", [mt.partial_S for mt in self.muc_tables])
        object.__setattr__(self, "related_As", [mt.related_A for mt in self.muc_tables])
        object.__setattr__(self, "related_Ss", [mt.related_S for mt in self.muc_tables])
        object.__setattr__(self, "missings", [mt.missing for mt in self.muc_tables])
        object.__setattr__(self, "spuriouses", [mt.spurious for mt in self.muc_tables])

    def get_global_statistics(
        self,
        comparison_type: int = MucTable.RELAXED_COMPARISON,
        with_help=False,
    ) -> dict[str, float]:
        object.__setattr__(self, "corrects", [mt.correct for mt in self.muc_tables])
        object.__setattr__(self, "incorrects", [mt.incorrect for mt in self.muc_tables])
        object.__setattr__(self, "partial_As", [mt.partial_A for mt in self.muc_tables])
        object.__setattr__(self, "partial_Ss", [mt.partial_S for mt in self.muc_tables])
        object.__setattr__(self, "related_As", [mt.related_A for mt in self.muc_tables])
        object.__setattr__(self, "related_Ss", [mt.related_S for mt in self.muc_tables])
        object.__setattr__(self, "missings", [mt.missing for mt in self.muc_tables])
        object.__setattr__(self, "spuriouses", [mt.spurious for mt in self.muc_tables])

        stats = {}
        stats["CORRECT"] = np.sum(self.corrects)
        stats["INCORRECT"] = np.sum(self.incorrects)
        stats["PARTIAL_ALLFRAGMENTS"] = np.sum(self.partial_As)
        stats["PARTIAL_SOMEFRAGMENTS"] = np.sum(self.partial_Ss)
        stats["PARTIAL"] = stats["PARTIAL_ALLFRAGMENTS"] + stats["PARTIAL_SOMEFRAGMENTS"]
        stats["RELATED_ALLFRAGMENTS"] = np.sum(self.related_As)
        stats["RELATED_SOMEFRAGMENTS"] = np.sum(self.related_Ss)
        stats["RELATED"] = stats["RELATED_ALLFRAGMENTS"] + stats["RELATED_SOMEFRAGMENTS"]
        stats["MISSING"] = np.sum(self.missings)
        stats["SPURIOUS"] = np.sum(self.spuriouses)
        stats["POSSIBLE"] = stats["CORRECT"] + stats["INCORRECT"] + stats["MISSING"] + stats["PARTIAL"] + stats["RELATED"]
        stats["ACTUAL"] = stats["CORRECT"] + stats["INCORRECT"] + stats["SPURIOUS"] + stats["PARTIAL"] + stats["RELATED"]
        stats["BORDER CORRECT"] = stats["CORRECT"] + stats["INCORRECT"]
        stats["INCORRECT_BORDER"] = stats["PARTIAL"] + stats["SPURIOUS"] + stats["RELATED"]
        stats["UNDERGENERATION"] = MucTable.safe_divide(
            stats["MISSING"],
            stats["POSSIBLE"],
        )
        stats["OVERGENERATION"] = MucTable.safe_divide(
            stats["SPURIOUS"],
            stats["ACTUAL"],
        )
        match comparison_type:
            case MucTable.RELAXED_COMPARISON:
                stats["RECALL"] = MucTable.safe_divide(
                    stats["CORRECT"] + stats["PARTIAL"] + stats["RELATED"] + stats["INCORRECT"],
                    stats["POSSIBLE"],
                )
                stats["PRECISION"] = MucTable.safe_divide(
                    stats["CORRECT"] + stats["PARTIAL"] + stats["RELATED"] + stats["INCORRECT"],
                    stats["ACTUAL"],
                )
                stats["SUBSTITUTION"] = MucTable.safe_divide(
                    stats["INCORRECT"] + stats["PARTIAL"] + stats["RELATED"],
                    stats["CORRECT"] + stats["PARTIAL"] + stats["RELATED"] + stats["INCORRECT"],
                )
            case MucTable.STRICT_COMPARISON:
                stats["RECALL"] = MucTable.safe_divide(
                    stats["CORRECT"],
                    stats["POSSIBLE"],
                )
                stats["PRECISION"] = MucTable.safe_divide(
                    stats["CORRECT"],
                    stats["ACTUAL"],
                )
                stats["SUBSTITUTION"] = MucTable.safe_divide(
                    stats["INCORRECT"],
                    stats["CORRECT"] + stats["PARTIAL"] + stats["RELATED"] + stats["INCORRECT"],
                )
            case MucTable.BORDER_COMPARISON:
                stats["RECALL"] = MucTable.safe_divide(
                    stats["BORDER CORRECT"],
                    stats["POSSIBLE"],
                )
                stats["PRECISION"] = MucTable.safe_divide(
                    stats["BORDER CORRECT"],
                    stats["ACTUAL"],
                )
                stats["SUBSTITUTION"] = MucTable.safe_divide(
                    stats["INCORRECT_BORDER"],
                    stats["BORDER CORRECT"] + stats["INCORRECT_BORDER"],
                )
        if stats["PRECISION"] + stats["RECALL"] != 0:
            stats["F1"] = (2 * stats["PRECISION"] * stats["RECALL"])/(stats["PRECISION"] + stats["RECALL"])
        else:
            stats["F1"] = 0.0
        if with_help:
            helping = "\nCORRECT = when annotation tags and indices match completely\n"
            helping += "INCORRECT = when annotation tags and attributes do not match, but the indices coincide\n"
            helping += "PARTIAL_ALLFRAGMENTS = when the annotation tags are the same but one of the annotations has the same end index and a different start index, for ALL fragments\n"
            helping += "PARTIAL_SOMEFRAGMENTS = same as previous, but for multi-fragment annotations with at least one CORRECT Fragment match\n"
            helping += "PARTIAL = PARTIAL_ALLFRAGMENTS + PARTIAL_SOMEFRAGMENTS\n"
            helping += "RELATED_ALLFRAGMENTS = when the annotation tags are different but one of the annotations has the same end index and a different start index, for ALL fragments\n"
            helping += "RELATED_SOMEFRAGMENTS = same as previous, but for multi-fragment annotations with at least one CORRECT Fragment match\n"
            helping += "RELATED = RELATED_ALLFRAGMENTS + RELATED_SOMEFRAGMENTS\n"
            helping += "MISSING = annotations existing only in the gold standard annotation set (aka. false negative)\n"
            helping += "SPURIOUS = annotations existing only in the candidate annotation set (aka. false positive)\n"
            helping += "\nPOSSIBLE = CORRECT + INCORRECT + MISSING + PARTIAL + RELATED\n"
            helping += "ACTUAL = CORRECT + INCORRECT + SPURIOUS + PARTIAL + RELATED\n"
            helping += "RECALL = (CORRECT + ~PARTIAL + ~RELATED + ~INCORRECT) / POSSIBLE\n"
            helping += "PRECISION = (CORRECT + ~PARTIAL + ~RELATED + ~INCORRECT) / ACTUAL\n"
            helping += "UNDERGENERATION = MISSING / POSSIBLE\n"
            helping += "OVERGENERATION = SPURIOUS / ACTUAL\n"
            helping += "SUBSTITUTION = (INCORRECT + ~PARTIAL + ~RELATED) / (CORRECT + PARTIAL + RELATED + INCORRECT) : (CORRECT + INCORRECT) / (CORRECT + INCORRECT + PARTIAL + SPURIOUS + RELATED) (for BORDER_COMPARISON)\n"
            helping += "F1-SCORE = 2 * PRECISION * RECALL / (PRECISION + RECALL)\n"
            helping += "BORDER CORRECT = CORRECT + INCORRECT\n"
            helping += "INCORRECT BORDER = PARTIAL + SPURIOUS + RELATED\n"
            helping += "\nCOMPARISON CONFIGURATIONS:\n"
            helping += "- RELAXED_COMPARISON = 1 (DEFAULT)\n"
            helping += "- STRICT_COMPARISON = 2\n"
            helping += "- BORDER_COMPARISON = 3\n"
            helping += "\n~PARTIAL and ~RELATED means it is considered only for RELAXED_COMPARISON config\n"
            helping += "~INCORRECT means it is considered only for BORDER_COMPARISON config\n"
            stats["Metrics HELP:"] = helping
        return stats
