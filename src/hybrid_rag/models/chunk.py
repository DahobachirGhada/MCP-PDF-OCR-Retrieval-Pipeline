from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    text: str                  # what the LLM will read
    context: str               # short header, used only when embedding
    metadata: dict = field(default_factory=dict)

    @property
    def embedding_text(self) -> str:
        return f"{self.context}\n\n{self.text}" if self.context else self.text