#! python3  # noqa: E265

"""
Minimalist slugifier.

Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import re
import unicodedata


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# for slugified
_regex_slugify_strip = re.compile(r"[^\w\s-]")
_regex_slugify_hyphenate = re.compile(r"[-\s]+")

# #############################################################################
# ########## Functions #############
# ##################################


def sluggy(text_to_slugify: str, replacer: str = "-") -> str:
    """Very basic slugifier using only Python Standard Library.

    Args:
        text_to_slugify (str): text to slugify
        replacer (str, optional): char used to replace special chars. Defaults to "-".

    Example:

    .. code-block:: python

        sample_txt = "Oyé oyé brâves gens de 1973 ! Hé oh ! Sentons-nous l'ail %$*§ ?!"
        print(sluggy(sample_txt))
        > oye-oye-braves-gens-de-1973-he-oh-sentons-nous-lail


    Returns:
        str: input character string stringified
    """
    slug = (
        unicodedata.normalize("NFKD", text_to_slugify)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    slug = _regex_slugify_strip.sub("", slug).strip().lower()
    slug = _regex_slugify_hyphenate.sub(replacer, slug)

    return slug


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
