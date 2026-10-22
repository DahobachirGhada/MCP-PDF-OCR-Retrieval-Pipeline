import re

SENTENCE_END = re.compile(r"(?<=[.!?؟…])\s+|\n+")


def normalize(text: str) -> str:
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)   # re-join words hyphenated at line end
    return " ".join(text.split())


def _hard_split(sentence: str, max_chars: int) -> list[str]:
    out = []
    while len(sentence) > max_chars:
        cut = sentence.rfind(" ", 0, max_chars)
        cut = cut if cut > 0 else max_chars
        out.append(sentence[:cut].strip())
        sentence = sentence[cut:].strip()
    out.append(sentence)
    return out


def split_text(text: str, max_chars: int, overlap: int) -> list[str]:
    sentences = [s.strip() for s in SENTENCE_END.split(text) if s.strip()]
    pieces = [p for s in sentences for p in _hard_split(s, max_chars)]

    chunks, current, size = [], [], 0
    for piece in pieces:
        if current and size + len(piece) + 1 > max_chars:
            chunks.append(" ".join(current))
            tail, tail_size = [], 0            # carry the last sentences forward
            for prev in reversed(current):
                if tail_size + len(prev) > overlap:
                    break
                tail.insert(0, prev)
                tail_size += len(prev) + 1
            current, size = tail, tail_size
        current.append(piece)
        size += len(piece) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks