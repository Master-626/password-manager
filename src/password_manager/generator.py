"""Password generation using the operating system's randomness via secrets."""

import secrets
import string


def generate_password(length: int = 20, symbols: bool = True) -> str:
    """Return a password containing each enabled character class.

    Rejection sampling preserves a uniform distribution over strings meeting
    the character-class requirement. There is no storage or network access.
    """
    if isinstance(length, bool) or not isinstance(length, int):
        raise ValueError("length must be an integer between 8 and 1024")
    if not 8 <= length <= 1024:
        raise ValueError("length must be between 8 and 1024")
    if not isinstance(symbols, bool):
        raise ValueError("symbols must be a boolean")

    groups = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        groups.append(string.punctuation)
    alphabet = "".join(groups)

    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if all(any(char in group for char in password) for group in groups):
            return password
