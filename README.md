# Python script for shortening journal names

This is a Python script that takes in 
- a .bib file with references, and  
- a .csv file with journal-abbreviation pairs,

and outputs 
- another .bib file with all journal names replaced by abbreviations, and
- a .log file detailing the changes.

The ams abbreviation csv file in this repository is obtained from [this site](https://abbrv.jabref.org/journals/) with minor edits to remove duplicates. You may replace it with your own csv file / update the csv file if you think additional journal-abbreviation pairs are needed.

## Example usage
```
python bib_cleaner.py --bib ref.bib --csv ams.csv
```