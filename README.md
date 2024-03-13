# Python script for shortening journal names

This is a Python script that takes in 
- a .bib file with references, and  
- a .csv file with journal name - abbreviation pairs,

and outputs 
- another .bib file with all journal names replaced by abbreviations, and
- a .log file detailing the changes.

The ams abbreviation csv file in this repository is obtained from [this site](https://abbrv.jabref.org/journals/) with minor edits to remove duplicates. You should, however, always make sure the .csv file contains the journal name - abbreviation pairs you want.

## Example usage
```
    python bib_cleaner.py --bib ref.bib --csv ams.csv
```