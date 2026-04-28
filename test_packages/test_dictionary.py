import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from packages.chd import Dictionary, Character, convert_pronunciations

path_dict = '/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/MCD.jsonl'
# path_dict = '/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/MCD.jsonl'
# path_dict = str(Path(__file__).parent.parent.resolve())+'/appdata/examples/mcd.txt'

def test_dict_empty():
    d=Dictionary('empty')
    assert len(d) == 0
    assert str(d) == '<empty> dictionary: 0 character entries'
    assert d.characters == []
    assert d.character_index == []
    assert d+d == d

def test_dict():
    d=Dictionary('Test')
    assert d.read(path_dict,file_format='jsonl')
    assert len(d) == 79
    assert len(set(d)) == 79
    assert len(d.characters) == 79
    assert len(d.character_index) == 79
    
    
def test_subset():
    d=Dictionary('Test')
    d.read(path_dict,file_format='jsonl')
    c = d.characters[0]
    assert d[c] == c
    assert isinstance(d[0],Character)
    assert isinstance(d[0:1],Dictionary)
    assert isinstance(d[d.characters[2]],Character)
    assert len(d[:10]) == 10
    assert len(d[d[:10].character_index]) == 10

def test_combine():
    d1=Dictionary('Test1')
    d1.read(path_dict,file_format='jsonl')
    d2=Dictionary('Test2')
    d2.read(path_dict,file_format='jsonl')
    assert d1.characters == d2.characters
    assert d1 == d2
    assert d1[0] == d2[0]
    assert d1.search('s')[1] == d2.search('s')[1]
    
def test_sort_combine():
    d1=Dictionary('Test1')
    d1.read(path_dict,file_format='jsonl')
    d2=Dictionary('Test2')
    d2.read(path_dict,file_format='jsonl')
    d2.sorting_key='simple'
    assert d1 == d2
    assert d1.characters != d2.characters
    assert set(d1.characters) == set(d2.characters)
    assert d1[0] != d2[0]
    assert d1.search('gan') == d2.search('gan')
    assert d1.search('s')[1] != d2.search('s')[1]

def test_search():
    d=Dictionary('Test')
    d.read(path_dict,file_format='jsonl')
    assert 3 == len(d.search('gan',exact=False).characters)
    
    s = d.copy().search('gan',exact=False)
    s[0].update(simple='干干')
    assert s.search('gan',exact=False)['干干'] != None
    assert d.search('gan',exact=False)['干干'] == None
    
    s = d.search('gan',exact=False)
    s[0].update(simple='干干')
    assert d.search('gan',exact=False)['干干'] != None
    

def test_adding():
    d1=Dictionary('Test1')
    d1.read(path_dict,file_format='jsonl')
    d2=Dictionary('Test2')
    d2.read(path_dict,file_format='jsonl')
    
    assert len(d1[0:3]-d1[0]) == 2
    assert len(d1['子'] + d2['干']) == 5
    
    assert len(d1[0] + d1['子'] + d2['干'] + d1[0]) == 6 
    assert len(d1['子'] + d1[0] + d2['干'] + d1[0]) == 6 
    assert len(d1[10] + d1['子'] + d2['干'] + d1[0]) == 7 
    
    assert len(d1[10] + d1[0]) == 2
    new_dict = d1[10] + d2[0] + d1[20] 
    assert len(new_dict) == 3
    assert new_dict.name == ""
    
    assert (new_dict + d1['子']).name == "Test1"
    assert (new_dict + d1['子'] + d2['干']).name == "Test1"
    assert len(new_dict) == 3
    assert new_dict.name == ""    
    
    
def test_index():
    d=Dictionary('Test')
    d.read(path_dict,file_format='jsonl')
    
    c=d.search('c')[0]
    i1=d.index(c)
    
    d.sorting_key='simple'
    i2=d.index(c)
    
    d.sorting_key='pronunciation'
    i3=d.index(c)
    
    assert i1!=i2
    assert i1==i3
    assert c==d[i3]
    assert len(d[i3-1:i3+2]) == 3
    