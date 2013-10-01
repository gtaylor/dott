"""
Contains a parent class which all commands should inherit from.
"""

from src.daemons.server.ansi import ANSI_NORMAL, ANSI_HI_WHITE, ANSI_HI_BLUE, remove_ansi_escape_seqs, ANSI_HI_YELLOW


class BaseCommand(object):
    """
    A command. All commands should sub-class this.

    :attr str name: The command name. IE: 'look'.
    :attr list aliases: Alternative ways to call the
        command (e.g. 'l', 'glance', 'examine').
    """

    name = None
    aliases = []

    def _get_header_str(self, header_text, header_text_color=ANSI_HI_YELLOW,
                        pad_char='=', pad_color=ANSI_HI_BLUE):
        """
        Forms and returns a standardized header string.

        :param header_text: The text to show in the header
            block.
        :param pad_char: The character to use to pad the header outside the
            header text block.
        :param pad_color: The ANSI sequence to apply to the padding.
        :rtype: str
        """

        buf = '\n' + pad_color + (pad_char * 3) + ANSI_HI_WHITE
        buf += '[' + header_text_color + \
               header_text + ANSI_HI_WHITE + \
               ']' + pad_color
        remaining = 80 - len(remove_ansi_escape_seqs(buf))
        buf += pad_char * remaining
        return buf + ANSI_NORMAL

    def _get_subheader_str(self, *args, **kwargs):
        """
        Forms and returns a standardized subheader string.
        See :py:meth:`_get_header_str` for signature.

        :rtype: str
        """

        kwargs['pad_char'] = '-'
        return self._get_header_str(*args, **kwargs)

    def _get_footer_str(self, pad_char='=', pad_color=ANSI_HI_BLUE):
        """
        Forms and returns a standardized footer string.

        :param pad_char: The character to use to form the footer.
        :param pad_color: The ANSI sequence to apply to the padding.
        :rtype: str
        """

        return '\n' + pad_color + (pad_char * 79) + ANSI_NORMAL