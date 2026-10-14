def _escape(cell: str) -> str:
    return cell.replace("|", "\\|")


def to_markdown(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header, *body = rows
    lines = [
        "| " + " | ".join(_escape(c) for c in header) + " |",
        "|" + "---|" * len(header),
    ]
    lines += ["| " + " | ".join(_escape(c) for c in r) + " |" for r in body]
    return "\n".join(lines)