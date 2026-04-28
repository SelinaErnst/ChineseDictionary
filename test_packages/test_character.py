import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from packages.chd import Dictionary, Character, convert_pronunciations
path_dict = '/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/MCD.jsonl'

def test_char():
    c = Character()
    assert c.uniq == (None,None,None)
    assert c.pinyin == ''
    assert str(c) == '〔   |   |   〕'
    assert len(set([c])) == 1
    assert c.to_dict() == {cat:None for cat in c.categories}
    
    d = Dictionary(characters=c)
    assert len(d) == 0
    d = Dictionary(characters=[c,c,c])
    assert len(d) == 0
    d = c+c
    assert len(d) == 0
    
def test_categories():
    c1=Character()
    assert type(c1.valid) == list
    assert c1._Character__default_info_categories['simple'] == str
    assert c1._Character__default_info_categories['traditional'] == str
    assert c1._Character__default_info_categories['pronunciation'] == str
    
def test_eq():
    c1 = Character(simple='x',traditional='x',pronunciation='x')
    c2 = Character(simple='x',traditional='x',pronunciation='x',german='x')
    assert c1 == c2
    assert len(set([c1,c2])) == 1
    assert list(set([c1,c2]))[0] == c1
    
    c3 = c1.update(simple='y')
    assert c1.entry['simple'] == c3.entry['simple']
    
    c3 = c1.copy().update(simple='z')
    assert c1.entry['simple'] != c3.entry['simple']
    assert c1.entry['simple'] == 'y'
    assert c3.entry['simple'] == 'z'
    
def test_merge():
    c1 = Character(simple='x',traditional='x',pronunciation='x')
    c2 = Character(needed_categories={'german':list},simple='x',traditional='x',pronunciation='x',german='x')
    c3 = c1.copy()
    c3.update_valid_categories(german=list)
    c3.update(simple='z',german='x')
        
    assert c1.entry['simple'] == 'x'
    assert c1.entry['german'] == None
    
    c1.merge(c2)
    assert c1.entry['german'] == 'x'
    
    c1.merge(c3)
    assert c1.entry['simple'] == 'x'
    
    c1.merge(c3, overwrite_all=True)
    assert c1.entry['simple'] == 'z'
    
        
def test_adding():
    d=Dictionary('Test')
    d.read(path_dict,file_format='jsonl')
    assert len(d) == 79
    
    new_dict = d[:3]
    assert len(new_dict) == 3
    
    c = Character()
    assert type(c+c) == Dictionary
    assert len(c+c) == 0
    assert (c+c+c).name == ""
        
    
    assert len(new_dict + c + c) == 3
    assert len(c + c + new_dict) == 3
    assert len(new_dict) == 3
    
    assert (c+c+new_dict).name == "Test"
    assert (new_dict+c).name == "Test"
    
def test_adding_2():
    c=Character(simple='x',traditional='x',pronunciation='x')
    
    assert c.uniq == ('x','x','x')
    assert len(c+c) == 1
    
    assert len(c+c.copy().update(german='x')) == 1
    assert (c+c.copy().update(german='x'))[0].entry['german'] == None
    assert c.entry['german'] == None
    
    c.update_valid_categories(german=list)
    assert (c.update(german='x') + c)[0].entry['german'] == 'x'
    assert c.entry['german'] == 'x'
    
    assert len(c + c.copy().update(update_dict={'simple':'y'})) == 2
    
    
def test_adding_entry():
    c=Character(needed_categories={'test':str},simple='this',test='Hi',notthere="bye")
    assert 'simple' in c.categories
    assert 'test' in c.categories
    assert 'notthere' not in c.categories
    assert c['simple'] == "this"
    assert c['notthere'] == None
    assert c.entry['test'] == 'Hi'
    assert len(c.entry[['simple','test','notthere']]) == 2
    
    c.update({'test':'Hi'})
    assert c['test'] == 'Hi'
    assert dict(c.entry)['test'] == 'Hi'
    assert c.entry['test'] == 'Hi'

    c.update({'notthere':"ciao"})    
    assert 'notthere' not in c.categories
    