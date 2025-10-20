from .possible_instructions import adjustables
from .convert_instructions import plecoformat
import csv
import re
# import functools
# import operator

# pr -> header when printed
# opt -> whatever version of the header is found in file
header_dict={
    'CHAR_SIMPL':{
        'pr':'SIMPLIFIED CHARACTER',
        'opt':['CHAR','SIMPL']},
    'CHAR_TRADI':{
        'pr':'TRADITIONAL CHARACTER',
        'opt':['TRAD','TRADI']},
    'CHAR_PRON':{
        'pr':'PRONUNCIATION',
        'opt':['PRON','PR']},
    'ENG':{
        'pr':'ENGLISH',
        'opt':['ENG']},
    'GER':{
        'pr':'GERMAN',
        'opt':['GER']},
    'MW':{
        'pr':'MEASURE WORD',
        'opt':['MW']},
    'RAD':{
        'pr':'RADICAL',
        'opt':['RAD']},
    'OPP':{
        'pr':'OPPOSITES',
        'opt':['OPP']},
    'STR':{
        'pr':'STROKES',
        'opt':['STROKES','STR']},
    'CL':{
        'pr':'CLASSIFIER',
        'opt':['CL','CLASSIFIER']},
    'VAR':{
        'pr':'VARIENTS',
        'opt':['VARIANTS','VAR']},
    'REL':{
        'pr':'RELATIVES',
        'opt':['RELATIVES','REL','EXAMPLES']},
    'WRD':{
        'pr':'WORDS',
        'opt':['WORDS','WORD','WRD']},
    'DIS':{
        'pr':'DISTINGUISH',
        'opt':['DISTINGUISH','OTHERS']},
    'DICT':{
        'pr':'DICTIONARY ENTRIES',
        'opt':['DICTIONARY ENTRIES','GRAMMAR DICTIONARY ENTRIES','DICT']},
    'COMP':{
        'pr':'COMPONENTS',
        'opt':['COMP','COMPONENTS']},
    'MNE':{
        'pr':'MNEOMICS',
        'opt':['MNEOMICS','MNE']},
    'USE':{
        'pr':'USE AS COMPONENT',
        'opt':['COMPONENT USAGE','USAGE','USE AS COMPONENT']},
    'ORG':{
        'pr':'ORIGINS',
        'opt':['ORG','ORIGINS']},
    'ANC':{
        'pr':'ANCIENT FORM',
        'opt':['ANCIENT FORM','ANC','ANCIENT']},
    'LIN':{
        'pr':'LINKS',
        'opt':['LINKS','LIN','LK']}
}


def map_head(search:str,n=0):
    
    result=[short for short,terms in header_dict.items() if search in terms['opt']]
    if len(result)==0: 
        print('SOMETHING IS WRONG with the entry')
        print(search,result,n)
    else: return result[0]

def get_symbols(char):
    # should return a list (len=2) 
    # of simplified and traditional character (if there)
    simpl_trad=re.findall('([\u4e00-\u9fff]+)',char)
    if len(simpl_trad)==1:
        # if only one chataczer -> will always be seen as simplified form
        simpl_trad+=['']
    elif len(simpl_trad)==0:
        simpl_trad=['','']
    elif len(simpl_trad)>2:
        print('WARNING: More than one symbol representation',simpl_trad)
    return simpl_trad

def splitting(string,search):
    i=string.find(search,1)
    if i>0:
        keep=[string[:i]]+splitting(string[i:],search)
        return keep
    else:
        return [string]
    
def read_plecotxt(file:str) -> list:
    """
    The file given should be a txt file as exported by Pleco. The delimiter is \t.
    The function will look for a number of different information in that file.  
    header: CHAR_SIMPL, CHAR_TRADI, CHAR_PRON, ENG, GER, MW, RAD, OPP, STR, CL, VAR, REL, WRD, DIS, DICT, COMP, MNE, USE, ORG, ANC, LIN
    ## Parameters
    - **file** : _str_    
    ## Returns
    - _list_  
        A List of dictionaries is returned. The keys of the dictionaries are the headers (see above). 
    
    """
    try:
        with open(file, newline='') as file:
            tsv_reader = csv.reader(file, delimiter='\t')
            pleco_entries=[]
            for row in tsv_reader:
                # for each character (tuple) there is a number of information taken from the file
                char=tuple(row[:2])
                char_meaning=row[2]   
                char_entry=[]
                # most relevant lines start with format for colored text in PLECO -> split lines 
                cs=plecoformat("color_start")
                for text in re.split(f'{cs}',char_meaning):
                    # remove any unnecessary (format) characters in text
                    text=re.sub('[\uea00-\ued00]','', text)
                    text=re.sub('|'.join(adjustables.values()),'', text)
                    # remove lines that are now empty 
                    if text!='':
                        # dont need title lines (INFORMATION, CHARACTER ...)
                        if not text.startswith('INF') or not text.startswith('CHAR'):
                            # when lines starts with 2-3 characters -> replace unicode character u25fc (◼) with : 
                            # for all lines -> seperate at : (but only first instance)
                            text=re.sub(r'([A-Z]{2,3})\s+(?:\u25fc)\s',r'\1: ',text).split(':',1)
                            # add resulting list to entry (list [head,info])
                            char_entry+=[text]
                # the assumption: we have exactly one header 
                # and one info entry (from one line in file) -> len(l)=2
                new_entry=[char,{text[0]: text[1].strip(' ') for text in char_entry if len(text)==2}] 
                # create list of new_entry: [(charsym,pron),{head:info,...}]
                pleco_entries.append(new_entry)
                # print(new_entry)

        dict_entry_list=[]
        number = 0
        for entry in pleco_entries:
            number+=1
            # each entry looks like: [(char,pron),{head:info,...}]
            meaning=entry[1]
            char,pron=entry[0]
            simpl,trad=get_symbols(char)
            clean_entry={h:None for h in header_dict.keys()}
            clean_entry['CHAR_SIMPL']=simpl
            clean_entry['CHAR_TRADI']=trad
            clean_entry['CHAR_PRON']=pron
            if all([test == "" for test in [simpl,trad,pron]]):
                print(f'WARNING: entry number ({number}) does not have proper headers.')
                continue
            for head,info in meaning.items():
                if head in header_dict['ANC']['opt']:
                    # for line with head ANC split at 'http' (keep http!)
                    elements=splitting(info,"http")
                    # remove empty list elements (e), remove space from start and end of info entries
                    # links are under the wrong category (header) -> need to be moved
                    ancient_forms,extracted_links=[],[]
                    for e in elements:
                        e=e.strip(' ')
                        if 'zi.tools' in e: extracted_links+=[e]
                        elif e!='': ancient_forms+=[e]
                    # in rare cases I might have forgottwen to delete stuff (at the very end)
                    rest=extracted_links[-1].split(' ',1)
                    last_link=rest[:1]
                    extracted_links=extracted_links[:-1]+last_link
                    # warning to at see if there is information left out because of this
                    c=", ".join([simpl, trad, pron])
                    if len(rest)>1: print(f'WARNING: character ({c}) has unrelevant text at the end. Check original file.')
                    # warning to at see if there is information left out because of this
                    # create dict with all relevant infos
                    clean_entry['ANC']=ancient_forms if len(ancient_forms)>0 else None
                    clean_entry['LIN']=extracted_links if len(extracted_links)>0 else None
                else:
                    # split all info entries at '·' or '◼' as separators
                    elements=re.split(r'\s*[·|◼]\s*',info)
                    # remove empty list elements (e), remove space from start and end of info entries
                    clean_elements=[e.strip(' ') for e in elements if e!='']
                    if clean_elements==[] or clean_elements==['']: clean_elements=None
                    if map_head(head,info) in ['ORG','STR']: clean_elements = clean_elements[0]
                    # create dict with all relevant infos 
                    clean_entry[map_head(head,info)]=clean_elements
            # # create list of all info entries
            dict_entry_list+=[clean_entry]
        return dict_entry_list
            
    except Exception as e:
        print(getattr(e, 'message', repr(e)))
    