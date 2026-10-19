"""Built-in training corpus for the tokenization experiment.

This is FICTIONAL sample data — entries from a made-up lighthouse keeper's log.
It is deliberately small, plain ASCII, and repetitive, so a few hundred BPE
merges visibly turn frequent words into single tokens. Characters outside it
(accents, emoji) are what the "characters seen in training" base alphabet cannot
represent. Nothing here is a claim about the world.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingCorpus:
    id: str
    title: str
    note: str
    text: str


SAMPLE_CORPUS_ID = "greyhaven-keepers-log"
SAMPLE_CORPUS_NOTE = "Fictional sample data: a made-up lighthouse keeper's log, plain ASCII."

_ENTRIES = [
    "The keeper lit the lantern at dusk. The tide was low and the wind came from the west.",
    "The keeper wound the clock and trimmed the wick. The lantern burned clear until dawn.",
    "At dawn the keeper put out the lantern and wrote the log. The tide turned at noon.",
    "Fog came in from the harbour. The keeper sounded the horn every two minutes until the fog lifted.",
    "The wind turned north. The keeper climbed the tower stairs and checked the lantern glass for salt.",
    "A fishing boat passed the harbour wall at dusk. The keeper lit the lantern early.",
    "The tide was high at midnight. The keeper watched the lantern and the clock until dawn.",
    "The keeper cleaned the lens, oiled the clock, and swept the tower stairs before dusk.",
    "Rain all day. The wind came from the west and the harbour was quiet. The lantern burned clear.",
    "The keeper wrote the log at dawn: tide low, wind west, lantern clear, fog none.",
    "The supply boat came at noon with oil for the lantern and bread for the keeper.",
    "The keeper keeps the lantern, the clock, and the log. The tide keeps its own time.",
]

SAMPLE_CORPUS = TrainingCorpus(
    id=SAMPLE_CORPUS_ID,
    title="Greyhaven Light keeper's log",
    note=SAMPLE_CORPUS_NOTE,
    text="\n".join(_ENTRIES),
)

_CORPORA = {SAMPLE_CORPUS_ID: SAMPLE_CORPUS}


def get_corpus(corpus_id: str = SAMPLE_CORPUS_ID) -> TrainingCorpus:
    try:
        return _CORPORA[corpus_id]
    except KeyError as exc:
        raise ValueError(f"unknown corpus '{corpus_id}'") from exc
