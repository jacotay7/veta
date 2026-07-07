#!/usr/bin/env python3
"""
Example script showing how to split a single-textbox LEAS response into
"self" and "other" parts before scoring.

This example uses:
- veta.item.Item
- veta.auto_self_other_item.attempt_auto_self_other

The goal is to take one free-text response, automatically separate the
parts that refer to the respondent from the parts that refer to the other
person, and then pass item.self_sentence and item.other_sentence into your
usual scoring workflow.
"""

from veta import Item, attempt_auto_self_other, setup_logging


QUESTION = (
    "You are sitting across from your best friend. They are looking down and "
    "say that their romantic partner just broke up with them. How would you "
    "feel, and how would they feel?"
)


FAKE_RESPONSES = [
    (
        "Easy",
        "I would feel shocked, worried, and protective. "
        "They would feel sad, embarrassed, and heartbroken.",
    ),
    (
        "Medium",
        "I would feel tense at first because I would want to help. "
        "They would feel lonely and ashamed that the breakup happened.",
    ),
    (
        "Hard",
        "At first I would feel upset for them, but if they said they were "
        "relieved I would feel confused and then relieved too. They might feel "
        "hurt at first, then calmer once they realize they are not being "
        "judged.",
    ),
]


def show_split(complexity: str, response: str) -> None:
    """Create an Item, split it automatically, and print the result."""
    item = Item(response)
    try:
        attempt_auto_self_other(item, lang="en")
    except RuntimeError as exc:
        print("Automatic split unavailable:")
        print(exc)
        print("Original response only:")
        print(response)
        print("-")
        return

    print(f"[{complexity}] Response:")
    print(response)
    print("Self:")
    print(item.self_sentence or "<empty>")
    print("Other:")
    print(item.other_sentence or "<empty>")
    print("-")


def main() -> None:
    setup_logging(level="INFO", console_level="INFO", file_level="DEBUG")

    print("LEAS self/other separation example")
    print("Question prompt:")
    print(QUESTION)
    print()
    print("The script below demonstrates how to turn one textbox response into")
    print("item.self_sentence and item.other_sentence before scoring.")
    print()

    for complexity, response in FAKE_RESPONSES:
        show_split(complexity, response)

    print("Next step:")
    print("Use item.self_sentence and item.other_sentence with your scoring modules.")


if __name__ == "__main__":
    main()