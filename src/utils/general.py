"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game. 
"""

def to_unicode(obj, encoding='utf-8'):
    """
    This decodes a suitable object to 
    the unicode format. Note that one
    needs to encode it back to utf-8 
    before writing to disk or printing.
    """
    if isinstance(obj, basestring) \
            and not isinstance(obj, unicode):
        try:
            obj = unicode(obj, encoding)
        except UnicodeDecodeError:
            raise Exception("Error: '%s' contains invalid character(s) not in %s." % (obj, encoding))
        return obj

def to_str(obj, encoding='utf-8'):
    """
    This encodes a unicode string
    back to byte-representation, 
    for printing, writing to disk etc.
    """
    if isinstance(obj, basestring) \
            and isinstance(obj, unicode):
        try:
            obj = obj.encode(encoding)
        except UnicodeEncodeError:
            raise Exception("Error: Unicode could not encode unicode string '%s'(%s) to a bytestring. " % (obj, encoding))
    return obj