"""Built-in sample corpus for the RAG experiment.

This is FICTIONAL sample data — a made-up bike shop's help-centre articles.
It exists so the experiment runs offline with known "gold" facts that the
break/fix challenges can check against. Nothing here is a claim about the world.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str


SAMPLE_CORPUS_ID = "ridgeline-help-centre"
SAMPLE_CORPUS_NOTE = "Fictional sample data: help-centre articles for a made-up bike shop."

SAMPLE_CORPUS: list[Document] = [
    Document(
        "returns",
        "Returns and refunds",
        "Ridgeline Bikes accepts returns of unused bikes within 30 days of delivery. "
        "Returned bikes must include the original packaging. "
        "Refunds go to the original payment method within 5 business days after the "
        "warehouse inspects the bike. Custom-built bikes cannot be returned.",
    ),
    Document(
        "warranty",
        "Warranty coverage",
        "Every Ridgeline frame carries a lifetime warranty against manufacturing defects "
        "for the original owner. Components such as brakes, gears, and tires are covered "
        "for 2 years. The warranty does not cover crash damage or normal wear. To file a "
        "claim, email photos of the damage and your order number to the support team.",
    ),
    Document(
        "battery",
        "E-Trail battery care",
        "The Ridgeline E-Trail battery is a 625 Wh lithium-ion pack. A full charge from "
        "empty takes about 4.5 hours with the included 4 A charger. For long-term storage, "
        "keep the battery between 40 and 60 percent charge in a cool, dry place. Do not "
        "charge the battery below 0 °C.",
    ),
    Document(
        "shipping",
        "Shipping and assembly",
        "Orders ship from the Toronto warehouse within 2 business days. Standard delivery "
        "within Canada takes 3 to 7 business days. Bikes arrive 85 percent assembled; you "
        "attach the handlebar, pedals, and front wheel. Express shipping costs extra.",
    ),
    Document(
        "sizing",
        "Frame sizing guide",
        "Ridgeline frames come in four sizes: S, M, L, and XL. Riders between 160 and "
        "170 cm usually fit a size S. Riders between 170 and 180 cm usually fit a size M. "
        "If you are between sizes, choose the smaller frame for a more agile ride.",
    ),
    Document(
        "service",
        "Tune-ups and service",
        "Bring your bike for a free tune-up within 60 days of purchase at any partner shop. "
        "After the free tune-up, Ridgeline recommends a service every 6 months or 1,000 km, "
        "whichever comes first. Tune-ups include brake adjustment, gear indexing, and a "
        "safety check.",
    ),
]


def get_corpus(corpus_id: str = SAMPLE_CORPUS_ID) -> list[Document]:
    if corpus_id != SAMPLE_CORPUS_ID:
        raise KeyError(f"unknown corpus: {corpus_id}")
    return SAMPLE_CORPUS
