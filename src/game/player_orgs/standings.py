"""
Various inter-organization standings functions and utilities.
"""

from src.daemons.server.ansi import ANSI_HI_CYAN, ANSI_HI_GREEN, ANSI_HI_WHITE, ANSI_NORMAL, ANSI_HI_YELLOW, ANSI_HI_RED


def get_standing_value_cosmetics(standing_val):
    """
    Given a standing value between 0.0 and 1.0, return a text label for the
    value and a color that may be optionally used.

    :param float standing_val: The standing value to return cosmetics for.
    :rtype: tuple
    :returns: A tuple in the format of (standing_name, standing_color).
    """

    if standing_val >= 0.9:
        return "Allied", ANSI_HI_GREEN
    elif standing_val >= 0.75:
        return "Friendly", ANSI_HI_CYAN
    elif standing_val > 0.5:
        return "Cordial", ANSI_HI_WHITE
    elif standing_val == 0.5:
        return "Neutral", ANSI_NORMAL
    elif standing_val >= 0.45:
        return "Disliked", ANSI_HI_YELLOW
    else:
        return "Hated", ANSI_HI_RED