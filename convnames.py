#!/usr/bin/python3
# This code is called by glibc.spec via lua to generate the mapping
# from language code to language name.  The code uses langtable to
# do the mapping.  The information in langtable is a harmonization
# of CLDR and glibc lang_name data.
import sys
try:
    import langtable
except ImportError:
    # if the import fails, don't translate anything
    langtable = None

for lang in sys.argv[1:]:
    if langtable:
        name = langtable.language_name(languageId=lang, languageIdQuery='en')
        print(name or lang)
    else:
        print(lang)
