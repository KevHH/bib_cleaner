import argparse
import pandas as pd
import datetime

def get_next_entry_indices(i:int, lines: list[str]):
    '''
        obtain starting and ending indices of the next bib entry
        
        Args:
            i: index to start the search, need to be smaller than len(lines)
            lines: list of strings, each corresponding to a line in the file

        Output:
            st: int, bib entry starting index
            ed: int, bib entry ending index
    '''
    if i >= len(lines):
        return None, None 
    
    # locate start of entry
    try:
        st = next(j+i for j, line in enumerate(lines[i:]) if "@" in line)
    except StopIteration:
        return None, None
    
    if st+1 > len(lines):
        raise ValueError('Bib entry started at the last line.')
    
    # move cursor to next bib entry or end of file
    try: 
        next_st = next(j+st+1 for j, line in enumerate(lines[st+1:]) if "@" in line)
    except StopIteration:
        next_st = len(lines)
    try: 
        # TO IMPROVE: this is a dirty line. It may catch an intermediate "}".
        ed = next(next_st - j for j, line in enumerate(lines[st+1:next_st].__reversed__()) if "}" in line)
    except StopIteration:
        raise ValueError('Bib entry started at line ' + str(st) + ' but no ending } found')
    
    return st, ed

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--bib', type=str, help='path to .bib file to clean', default='ref.bib',
                    required=False)
parser.add_argument('--csv', type=str, default='ams.csv',
                    help='path to .csv file with two columns, one for journal names and one for abbreviations. No header allowed.',
                    required=False)
parser.add_argument('--output', type=str,
                    help='path to output .bib file. (default: .bib file name with "_output").',
                    required=False)
args = parser.parse_args()

if args.output is None: 
    args.output = args.bib.split('.')[0] + '_output.bib'
log_path = args.output.split('.')[0] + '_' + datetime.datetime.now().isoformat() + '.log'

# convert csv to dictionary
df = pd.read_csv(args.csv, header=None)
if len(df.columns) != 2:
    raise ValueError('2 columns expected but ' + str(len(df)) + ' column(s) found, exiting.')

# ignore case
df[0] = df[0].str.lower()

if len(df[0][df[0].duplicated()]) > 0:
    raise ValueError('csv file contains duplicated entries, exiting.')
abbrv = df.set_index(0).T.to_dict('records')[0]
abbrv_items = df[1].str.lower().to_list()

# read .bib file
with open(args.bib, 'r') as f:
    lines = f.readlines()

processed_lines = lines.copy()
replaced_log = []
not_replaced_log = []
arxiv_log = []
update_csv_log = []

st, ed = get_next_entry_indices(0, lines)
while st is not None and ed is not None:
    entry_name = lines[st].split('{')[-1].split(',')[0]
    
    # search for journal line to be replaced
    try:
        index = next(j+st for j, line in enumerate(lines[st:ed+1]) if "journal=" in line)
    except StopIteration:
        # no journal entry found, skip
        st, ed = get_next_entry_indices(ed, lines)
        continue
    
    # split only at the first = sign
    line_info = lines[index].strip().split('=', 1)
    journal = line_info[1].split('{',1)[1].rsplit('}',1)[0]
    j_lower = journal.lower()
    
    if j_lower in abbrv.keys():
        processed_lines[index] = lines[index].replace(journal, abbrv[j_lower])
        replaced_log.append('  - line ' + str(index) + ', entry "' + entry_name + '", "' 
                                + journal + '" --> "' + abbrv[j_lower] + '"\n' )
    elif 'arxiv' in j_lower:
        arxiv_log.append('  - line ' + str(index) + ', entry "' + entry_name + '", "' 
                                + journal + '"\n' )
    elif j_lower not in abbrv_items and '.' not in journal:
        update_csv_log.append('  - line ' + str(index) + ', entry "' + entry_name + '", "' 
                                + journal + '"\n' )
    else:
        not_replaced_log.append('  - line ' + str(index) + ', entry "' + entry_name + '", "' 
                                    + journal + '"\n' )
    
    # go to next entry
    st, ed = get_next_entry_indices(ed, lines)

with open(args.output, 'w+') as f:
    f.writelines(processed_lines)

with open(log_path, 'w+') as f:
    f.writelines(  [ '[Replaced entries]\n' ]
                   + replaced_log  
                   + [ '\n', '\n' ] 
                   + [ '[Not replaced -- arXiv entries]\n' ]
                   + arxiv_log
                   + [ '\n', '\n' ] 
                   + [ '[Not replaced -- may need abbreviations for these articles?]\n' ]
                   + update_csv_log
                   + [ '\n', '\n' ] 
                   + [ '[Not replaced -- remaining entries]\n' ]
                   + not_replaced_log
    )

print('Replaced ' + str(len(replaced_log)) + ' entries.\n' 
      + 'Found ' + str(len(arxiv_log)) + ' arXiv entries.\n'
      + 'Additional abbreviations may be needed for ' + str(len(update_csv_log)) + ' entries.\n' 
      + 'Check ' + log_path + ' for details.')