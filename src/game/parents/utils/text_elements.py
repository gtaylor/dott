"""
Assorted standardized text elements like progress bars, graphs/charts,
headers, etc.
"""

import math
from src.daemons.server.ansi import ANSI_HI_WHITE, ANSI_HI_GREEN, ANSI_HI_YELLOW, ANSI_HI_RED, ANSI_GREEN, ANSI_NORMAL, ANSI_YELLOW, ANSI_RED


def progress_bar_str(char_limit, max_value, current_value):
    """
    Returns a pretty progress bar string, complete with colorization.

    :param int char_limit: How wide the progress bar (in characters) should
        be. This includes the bar and its brackets. Must be at least 6.
    :param int max_value: The maximum numeric value for the data represented
        in the bar.
    :param int current_value: The current value for the value represented
        in the bar.
    :rtype: basestring
    :returns: A properly formatted progress bar.
    """

    assert char_limit > 6, "Bars must be at least 6 characters wide."

    max_bar_width = char_limit - 2
    perc = float(current_value) / max_value
    bar_width = int(math.floor(perc * max_bar_width))
    if perc >= 0.9:
        bar_color = ANSI_HI_GREEN
    elif perc >= 0.75:
        bar_color = ANSI_NORMAL + ANSI_GREEN
    elif perc >= 0.5:
        bar_color = ANSI_HI_YELLOW
    elif perc >= 0.3:
        bar_color = ANSI_NORMAL + ANSI_YELLOW
    elif perc >= 0.2:
        bar_color = ANSI_HI_RED
    else:
        bar_color = ANSI_NORMAL + ANSI_RED

    buf = ANSI_HI_WHITE + '[' + bar_color
    buf += ('=' * bar_width) + (' ' * (max_bar_width - bar_width))
    buf += ANSI_HI_WHITE + ']' + ANSI_NORMAL
    return buf, int(math.floor(perc * 100)), bar_color