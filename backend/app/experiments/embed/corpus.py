"""Built-in sample library for the embeddings experiment.

FICTIONAL/GENERIC sample sentences in four topics. They exist so the experiment
runs offline with known categories the challenges can check against. Several
pairs say the same thing with no words in common, which is exactly where a
lexical embedder fails and a neural one should not. Nothing here is a claim
about the world.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: str
    category: str
    text: str


SAMPLE_LIBRARY_ID = "four-topics"
SAMPLE_LIBRARY_NOTE = "Sample sentences in four topics. Generic examples, not claims about the world."
CATEGORIES = ("animals", "food", "furniture", "vehicles")

SAMPLE_LIBRARY: list[Item] = [
    Item("animals-1", "animals", "The dog chased a ball across the yard."),
    Item("animals-2", "animals", "A kitten slept curled up on the windowsill."),
    Item("animals-3", "animals", "Wolves hunt together in packs through the winter forest."),
    Item("animals-4", "animals", "The parrot learned to repeat a few words."),
    Item("animals-5", "animals", "A horse grazed quietly in the green field."),
    Item("animals-6", "animals", "Our puppy fetches sticks and brings them back."),
    Item("food-1", "food", "She baked a loaf of sourdough bread this morning."),
    Item("food-2", "food", "The soup needs more salt and a little pepper."),
    Item("food-3", "food", "Fresh strawberries are sweet in early summer."),
    Item("food-4", "food", "He grilled vegetables and served them with rice."),
    Item("food-5", "food", "A bowl of noodles makes a warm dinner."),
    Item("food-6", "food", "Dessert was a slice of chocolate cake."),
    Item("furniture-1", "furniture", "The oak table seats eight people."),
    Item("furniture-2", "furniture", "A soft armchair stands beside the fireplace."),
    Item("furniture-3", "furniture", "The bookshelf is full of old novels."),
    Item("furniture-4", "furniture", "We bought a new mattress for the guest bed."),
    Item("furniture-5", "furniture", "The desk has three drawers and a lamp."),
    Item("furniture-6", "furniture", "A wooden stool sits under the kitchen counter."),
    Item("vehicles-1", "vehicles", "The train left the station ten minutes late."),
    Item("vehicles-2", "vehicles", "He rides his bicycle to work every day."),
    Item("vehicles-3", "vehicles", "The truck delivered furniture across town."),
    Item("vehicles-4", "vehicles", "A small plane landed on the grass runway."),
    Item("vehicles-5", "vehicles", "The bus was crowded during rush hour."),
    Item("vehicles-6", "vehicles", "She parked the electric car in the garage."),
]


def get_library(library_id: str = SAMPLE_LIBRARY_ID) -> list[Item]:
    if library_id != SAMPLE_LIBRARY_ID:
        raise KeyError(f"unknown library: {library_id}")
    return SAMPLE_LIBRARY
