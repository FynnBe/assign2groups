import argparse
import csv
import numpy
import logging

from pathlib import Path
from scipy.optimize import linear_sum_assignment


logger = logging.getLogger(__name__)


def assign2groups(file_path: Path, bad_assignment_cost=255):
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    with file_path.open(encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        groups = next(reader)
        cell00 = groups.pop(0)
        broken_groups = [g for g in groups if "=" not in g]
        if broken_groups:
            raise ValueError(
                f"Missing group size (indicated by '<group name>=<group size>', e.g. GroupA=3) for:\n{broken_groups}"
            )

        group_names, group_sizes = zip(*[g.split("=") for g in groups])
        broken_group_idx = [i for i, g in enumerate(group_sizes) if not g.isdigit()]
        if broken_group_idx:
            raise ValueError(
                f"Wrong group size format (indicated by <group name>=<group size>, e.g. GroupA=3) for:\n"
                f"{[groups[i] for i in broken_group_idx]}"
            )

        preferences = [entry for entry in reader]

    group_sizes = [int(s) for s in group_sizes]
    logger.debug("group sizes: %s", group_sizes)
    group_index = numpy.cumsum([0] + group_sizes)
    logger.debug("group index: %s", group_index)
    if len(preferences) > group_index[-1]:
        raise ValueError(
            f"Too many participants ({len(preferences)}) for too little group capacity "
            f"({'+'.join(str(gs) for gs in group_sizes)} = {group_index[-1]})"
        )

    group_number_from_index = numpy.empty(group_index[-1], dtype=numpy.int)
    for i in range(len(group_index) - 1):
        group_number_from_index[group_index[i] : group_index[i + 1]] = i

    logger.debug("group number from index: %s", group_number_from_index)

    costs = numpy.full(shape=(len(preferences), group_index[-1]), fill_value=bad_assignment_cost, dtype=numpy.uint8)
    names = []
    for i, pref in enumerate(preferences):
        names.append(pref.pop(0))
        for j, p in enumerate(pref):
            if p:
                costs[i, group_index[j] : group_index[j + 1]] = p

    logger.debug("costs\n%s", costs)
    row_ind, col_ind = linear_sum_assignment(costs)
    logger.debug("row_ind %s, assoc. names: %s", row_ind, [names[ri] for ri in row_ind])
    logger.debug("col_ind %s, assoc. group nr: %s", col_ind, group_number_from_index[col_ind])
    logger.debug("global cost: %d", costs[row_ind, col_ind].sum())
    logger.info("average assigned preference: %.2f", costs[row_ind, col_ind].mean())

    suffix = file_path.suffix
    file_stem = file_path.stem
    export_file_path = file_path.parent / f"{file_stem}_assigned{suffix}"
    logger.info("write result to %s", export_file_path)
    assigned_sizes = dict(zip(*numpy.unique(group_number_from_index[col_ind], return_counts=True)))
    logger.debug("assigned sizes: %s", assigned_sizes)
    with export_file_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([cell00] + [f"{gn}={assigned_sizes.get(gi, 0)}" for gi, gn in enumerate(group_names)])
        for ci, ri in zip(col_ind, row_ind):
            writer.writerow([names[ri]] + [""] * group_number_from_index[ci] + [costs[ri, ci]])


def main():
    parser = argparse.ArgumentParser(description="Assign participants to groups.")
    parser.add_argument(
        "csv_file",
        type=Path,
        help="First row must contain group names and sizes (in the format '<group name>=<group size>', e.g. "
        "'Group A=5' from the second column on. Second row downwards should contain participant names in the first "
        "column and their preferences (0 (highest) to 255 (lowest)) for each group. Preferences do not need to be "
        "complete, nor start at 0, e.g. Name,Preferences: 'Name,1,,,1,3,9' is a valid input for a row.",
    )
    parser.add_argument(
        "--log-level", default="info", choices=["debug", "info", "warning", "error", "critical"], help="Log level"
    )
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s:%(message)s", level=getattr(logging, args.log_level.upper()))
    assign2groups(args.csv_file)
