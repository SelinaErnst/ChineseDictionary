import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from packages.chd import convert_pronunciations

def test_convert_pron():
    s = convert_pronunciations('阝ljscac [ba1ba]')
    assert '[bāba]' in s
    s = convert_pronunciations('阝ljscac [ba1 ba]')
    assert '[bāba]' in s
    s = convert_pronunciations('阝ljscac [八ba1ba2]')
    assert '[八ba1ba2]' in s
    s = convert_pronunciations('阝ljscac [ba1ba2八]')
    assert '[ba1ba2八]' in s