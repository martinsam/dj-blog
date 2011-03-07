# -*- coding: utf-8 -*-
import string
import re
from bleach import Bleach
# django stuff
from django.utils.html import strip_tags, linebreaks
from django.utils.text import normalize_newlines
from django.utils.encoding import force_unicode

ALLOWED_TAGS = [
    'a',
    'b',
    'code',
    'em',
    'i',
    'strong',
]

def strip_punctuation(input):
    """
    Strip punctuation and words with a length lower than 2 chars
    """
    
    exclude = set( string.punctuation )
    
    # http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
    letters = []
    for s in input:
        if s in exclude:
            letters.append(' ')
        else:
            letters.append(s)
    
    words = ''.join(s for s in letters)
    
    words_list = words.split()
    
    # delete words with length < 2 chars
    filtered_words_list = []
    for w in words_list:
        if w.isdigit() or len(w) > 2:
            filtered_words_list.append(w)
    
    return ' '.join(s for s in filtered_words_list)


def wordify(input):
    input = strip_tags( input )
    input = re.sub(r'&(?:\w+|#\d+);', ' ', force_unicode(input)) # replace entities by a space
    input = strip_punctuation( input )
    input = normalize_newlines( input )
    input = force_unicode( re.sub(r'\s+', ' ', input) )
    input = input.lower()
    return input


def sanitize_html(input):
    # HTML sanitizer and auto-linker
    # http://coffeeonthekeyboard.com/bleach-html-sanitizer-and-auto-linker-for-django-344/
    bl = Bleach()
    cleaned_input = bl.clean( input, tags=ALLOWED_TAGS )
    cleaned_input = bl.linkify( cleaned_input )
    cleaned_input = linebreaks( cleaned_input )# linebreaks converts newlines into <p> and <br />s.
    return cleaned_input


