import re


def _clean_cell(value) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def clean_table(df) -> list[list[str]]:
    rows = [[_clean_cell(c) for c in row] for row in df.values.tolist()]
    rows = [r for r in rows if any(r)]                  # drop empty rows
    if not rows:
        return []

    keep = [i for i in range(len(rows[0])) if any(r[i] for r in rows)]
    return [[r[i] for i in keep] for r in rows]         # drop empty columns