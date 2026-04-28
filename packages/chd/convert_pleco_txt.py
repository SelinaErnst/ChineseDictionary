# from .printentry import encode_pinyin
from .unicode_characters import chinese_char,not_chinese_char,pleco_char
from .unicode_characters import PinyinToneMark
from .character import Character
import re
import os
import json
from pathlib import Path
from typing import Literal, TypeAlias

APP_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
def load_json(path, default_dir=APP_DIR):
    path=path if default_dir==None else Path(default_dir)/path
    with open(path, "r") as f:
        settings = json.load(f)
    return settings

_PLECO_COMMAND: TypeAlias = Literal[
    'newline', 'tab', 'point', 'dot',
    'bracket', 'link', 'italic', 'underline','bold','narrow_bold','slightly_bold','bg',
    'textsmall','textbig','color','block',
    'left','right','indent','mark','markline',
    'line'
    ]
_PLECO_SYNTAX = load_json('pleco_syntax.json',APP_DIR/'appdata'/'defaults')

_CHD_COLOR = load_json('pleco_colors.json',APP_DIR/'appdata'/'colors')
_PLECO_COLOR = load_json('possible_colors.json',APP_DIR/'appdata'/'colors')
_CHD_COLOR.update(_PLECO_COLOR)

_CHD_FONT_MAP={
    'normal':['normal','n','none'],
    'bold':['bold','b'],
    'narrow_bold':['narrow_bold','nb'],
    'slightly_bold':['slightly_bold','sb'],
    'italic':['italic','i'],
    'underline':['underline','u']}

_CHD_SIZE_MAP={
    'normal':['normal','none','n'],
    'textbig':['textbig','b','big'],
    'textsmall':['textsmall','s','small']
}

_CHD_LINE_MAP={
    'normal':['normal','l','none','n'],
    'newline':['newline','nl']    
}

_CHD_SEP_MAP={
    'normal':['normal','none','','n'],
    'dot':['dot','d'],
    'point':['point','p']
}

_CHD_VIS_MAP={
    'hidden': ['hidden','h','hid'],
    'ignore': ['ignore','i','ign'],
    'visible': ['visible','v','vis'],
    'available': ['available','a','av']
}

def is_size(size:str):
    return any([size in variants for variants in _CHD_SIZE_MAP.values()])
def is_command(command:_PLECO_COMMAND):
    return command in _PLECO_SYNTAX
def is_color(color:str):
    if isinstance(color,str) and color in _CHD_COLOR.values(): return True
    else: return False
def is_color_name(name:str):
    return name in _CHD_COLOR
def is_font(font:str):
    return any([font in f_variants for f_variants in _CHD_FONT_MAP.values()])
def is_empty(content:str):
    empty=(content=="") or (content==convert_to_pleco_syntax('newline'))
    return empty
        
def get_spec(spec_input,spec_map:dict):
    spec = [spec for spec,variants in spec_map.items() if spec_input in variants]
    if spec!=[]: return spec[0]
    else: return None
def get_font(font:str|None=None):
    font = get_spec(spec_input=font,spec_map=_CHD_FONT_MAP)
    if font=='normal': font=None
    return font
def get_color(color:str|None=None):
    if not is_color(color) or color=='none': color=None
    return color
def get_size(size:str=None):
    size = get_spec(spec_input=size,spec_map=_CHD_SIZE_MAP)
    if size=='normal': size=None
    return size
def get_line(line:str=None):
    line = get_spec(spec_input=line,spec_map=_CHD_LINE_MAP)
    if line=='newline': line=True
    else: line=False
    return line
def get_sep(sep:str=None):
    sep = get_spec(spec_input=sep,spec_map=_CHD_SEP_MAP)
    if sep=='normal': sep=None
    return sep
def get_vis(vis:str=None):
    vis = get_spec(spec_input=vis,spec_map=_CHD_VIS_MAP)
    if vis==None: vis='visible'
    return vis

_CHD_VISIBILITY: TypeAlias = Literal['hidden','ignore','visible','available']
def is_visible(vis:_CHD_VISIBILITY):
    vis = get_vis(vis)
    if vis in ['hidden','ignore']: return False
    elif vis in ['visible','available']: return True
    else: return True


_CONTAINER: TypeAlias = Literal['H','L','I','T']
def create_container(typ:_CONTAINER,text:str='DEFAULT',helper:bool=False,brackets:bool=True,**specs):
    def specs_are_specified(names):
        return all([name in specs for name in names])
    def get_specs(names):
        return '|'.join([specs.pop(name) for name in names])
    if typ=='H': 
        spec_names = ['font','color','visibility']
        default = ['n','none','visible']
    elif typ=='L': 
        spec_names = ['sep','newline','size']
        default = ['dot','l','normal']
    elif typ in ['T','I']: 
        spec_names = ['font','color','size']
        default = ['n','none','normal']
    else: 
        spec_names = []
        default = ['normal','normal','normal']
    if helper: default = spec_names
    if specs_are_specified(spec_names): specs=get_specs(spec_names)
    else: specs=default
    specs='|'.join(specs)
    container=f'{typ}:[{specs}]:{text}'
    if brackets: return f'<{container}>'
    else: return f'{container}'


def decode_pinyin(s):
    # ba1 -> bā, nv3 -> nǚ
    s = "" if s==None else s
    s = s.replace('ü','v')
    words = str(s).split(' ')
    result = []
    for s  in words:
        if s!=None and re.search(r'\d', s):
            s = s.lower()
            r = ""
            t = ""
            for c in s:
                if c >= 'a' and c <= 'z':
                    t += c
                elif c == ':':
                    assert t[-1] == 'u'
                    t = t[:-1] + "\u00fc"
                else:
                    if c >= '0' and c <= '5':
                        tone = int(c) % 5 # tone 5 -> 0
                        if tone != 0:
                            m = re.search("[aoeiuv\u00fc]+", t)
                            if m is None:
                                t += c
                            elif len(m.group(0)) == 1:
                                t = t[:m.start(0)] + PinyinToneMark[tone][PinyinToneMark[0].index(m.group(0))] + t[m.end(0):]
                            else:
                                if 'a' in t:
                                    t = t.replace("a", PinyinToneMark[tone][0])
                                elif 'o' in t:
                                    t = t.replace("o", PinyinToneMark[tone][1])
                                elif 'e' in t:
                                    t = t.replace("e", PinyinToneMark[tone][2])
                                elif t.endswith("ui"):
                                    t = t.replace("i", PinyinToneMark[tone][3])
                                elif t.endswith("iu"):
                                    t = t.replace("u", PinyinToneMark[tone][4])
                                else:
                                    t += "!"
                    r += t
                    t = ""
            r += t
            result+=[r]
        else:
            s=s.replace('v','ü')
            result+=[s]
    return ''.join(result)
    
def encode_pinyin(pinyin: str) -> str:
    # bā -> ba1
    if pinyin!=None:
        tone_map = {
            'ā': ('a', '1'), 'á': ('a', '2'), 'ǎ': ('a', '3'), 'à': ('a', '4'),
            'ē': ('e', '1'), 'é': ('e', '2'), 'ě': ('e', '3'), 'è': ('e', '4'),
            'ī': ('i', '1'), 'í': ('i', '2'), 'ǐ': ('i', '3'), 'ì': ('i', '4'),
            'ō': ('o', '1'), 'ó': ('o', '2'), 'ǒ': ('o', '3'), 'ò': ('o', '4'),
            'ū': ('u', '1'), 'ú': ('u', '2'), 'ǔ': ('u', '3'), 'ù': ('u', '4'),
            'ǖ': ('v', '1'), 'ǘ': ('v', '2'), 'ǚ': ('v', '3'), 'ǜ': ('v', '4'),
            'ü': ('v', ''),  # plain ü → v0
        }
        result = ""
        tone_digit = ""
        for c in pinyin:
            if c in tone_map:
                base, tone = tone_map[c]
                result += base
                tone_digit = tone
            else:
                # words can be seperated by space
                if (c == ' ') and tone_digit:
                    result += tone_digit
                    tone_digit = ""
                result += c
        if tone_digit:
            result += tone_digit
        return result


def convert_pronunciations(text:str):
    
    def pyinyin_to_string(match):
        naked_string = match.group().lstrip('[').rstrip(']')
        pinyin_string = decode_pinyin(naked_string)
        return f'[{pinyin_string}]'
    
    pattern = rf'\[([{not_chinese_char}]+)\]'
    text=re.sub(pattern,pyinyin_to_string,text)
    return text

    
def link_pronunciations(text:str):
    
    def link_to_string(match):
        naked_string = match.group().lstrip('[').rstrip(']')
        linked_string = convert_to_pleco_syntax('link',naked_string)
        return f'[{linked_string}]'
    
    pattern = rf'\[([{not_chinese_char}]+)\]'
    text=re.sub(pattern,link_to_string,text)
    return text
     
def frame_text(text:str|None,command:_PLECO_COMMAND,**kwargs):
    if text==None: text=""
    if not is_command(command): return f'{text}'
    else: syntax=_PLECO_SYNTAX[command]
        
    def color_frame(text=None,color=None,color_name=None):
        start,end = _PLECO_SYNTAX['color']
        if color_name!=None and is_color_name(color_name): 
            color=_CHD_COLOR[color_name]
        if color!=None and is_color(color): 
            return f'{start}{color}{text}{end}'
        else: return f'{text}'
    
    if command=='color':
        return color_frame(text=text,**kwargs)
    elif isinstance(syntax,list):
        start,end = syntax
        return f'{start}{text}{end}'
    else: return f'{syntax}{text}'

def convert_to_pleco_syntax(command,text="",**kwargs):
    
    def get_command(command:list):
        if len(command)>=2:
            first_command=command[0]
            if len(command)==2: rest_command=command[1] 
            else: rest_command=command[1:]
        elif len(command)==1:
            first_command=None
            rest_command=command[0]
        return first_command, rest_command
    
    
    if isinstance(command,str) or command==None:
        return frame_text(text=text,command=command,**kwargs)
    elif isinstance(command,list):
        first_command,command=get_command(command)
        if first_command!=None: text=frame_text(text=text,command=first_command,**kwargs)
        return convert_to_pleco_syntax(command=command, text=text,**kwargs)        
    else:
        print(f'WARNING: command "{command}" is not valid')
        return text

class Header():
    
    def __init__(self,container:str):
        cont_name,specs,self.text=self.__get_specs(container=container)
        self.__font,self.__color,self.__visible = specs.split('|')
        self.__font=get_font(self.__font)
        self.__color=get_color(self.__color)
        self.__visible=get_vis(self.__visible)
    
    @property
    def visible(self):
        # True for: visible, available
        # False for: ignore, hidden (don't print header)
        return is_visible(self.__visible)
    
    @property
    def default(self):
        return create_container(typ='H',helper=False,brackets=False) 
    
    def __get_specs(self,container:str):
        if len(container.split(':')) !=3: container=self.default
        container_specs=re.match(r'(.*?):\[(.*?)\]:(.*)',container).groups()
        return container_specs

    def write(self):
        if self.visible:
            return convert_to_pleco_syntax(
                command=[self.__font,'color'],text=self.text,color_name=self.__color)
        else: return ""
        
    def write_with_content(self,content:str):
        # decides whether content following header is printed
        # True for: visible (always), hidden, available (based on content)
        
        written=True
        if self.__visible in ['visible']: written=True
        elif self.__visible in ['ignore']: written=False
        elif self.__visible in ['available','hidden']: written=(not is_empty(content))
        
        if written:
            text=self.write()+content
            if self.visible: text+=convert_to_pleco_syntax('newline')
        else: text=""
        return text
    
    
class Content():
    
    def __init__(self,container,character:Character):
        self.__kind,specs,self.__content_name=self.__get_specs(container=container)
        if character!=None: self.content = character[self.__content_name]
        else: self.content = self.__content_name
        if self.__kind.startswith('T') or self.__kind.startswith('I'):
            self.__font,self.__color, self.__size = specs
        elif self.__kind.startswith('L'):
            self.__sep,self.__newline, self.__size = specs
        
        if hasattr(self,'_Content__font'): self.__font=get_font(self.__font)
        if hasattr(self,'_Content__color'): self.__color=get_color(self.__color)
        if hasattr(self,'_Content__size'): self.__size=get_size(self.__size)
        if hasattr(self,'_Content__newline'): self.__newline=get_line(self.__newline)
        if hasattr(self,'_Content__sep'): 
            self.__sep=get_sep(self.__sep)
            if self.__sep==None: self.bullet=""
            elif is_command(self.__sep): self.bullet = convert_to_pleco_syntax(self.__sep)
    
    @property
    def default(self):
        return create_container(typ=self.__kind,helper=False,brackets=False)    
        
    def __get_specs(self,container):
        container_specs = container.split(':')
        if len(container_specs)!=3: 
            if container.startswith('T'): self.__kind='T'
            else: self.__kind='L'
            container_specs=self.default
            
        self.__pattern=r'\[(.*)\|(.*)\|(.*)\]'
        specs = re.match(self.__pattern,container_specs[1]).groups()
        return (container_specs[0],specs,container_specs[2])
    
    def write(self):
        # text=""
        if self.content != None:
            if self.__kind.endswith('LINK'):
                if isinstance(self.content,list): 
                    self.content = [convert_to_pleco_syntax('link',e) for e in self.content]
                else: convert_to_pleco_syntax('link',self.content)
            if self.__kind.startswith('L'):
                text = self.create_list()
                text = convert_to_pleco_syntax(self.__size,text)
            elif self.__kind.startswith('T') or self.__kind.startswith('I'):
                text = self.create_text()
        else: text=""
        return text
                
                    
    def create_list(self):
        if isinstance(self.content,list):
            self.content = [e for e in self.content if e!=""]
            if self.content == []: return ""
            if self.bullet!="": self.bullet=self.bullet+' '
            if self.__newline:
                newline=convert_to_pleco_syntax('newline')
                combined_content=f'{newline}{self.bullet}'.join(self.content)
            else:
                combined_content=f' {self.bullet}'.join(self.content)
            if self.__sep == "point": combined_content=f'{self.bullet}'+combined_content
            return combined_content
        elif self.content==None: return ""
        else: return str(self.content)
        
    def create_text(self):
        if self.content==None: return ""
        else: 
            text=convert_to_pleco_syntax(
                command=[self.__size,self.__font,'color'],
                text=self.content,
                color_name=self.__color)
            return text
    
class Block():
    def __init__(self,command,character:Character):
        self.content=''
        self.block_command=command
        self.__character=character
    
    def write(self):
        if len(self.content.replace(convert_to_pleco_syntax('newline'),'')) == 0:
            return ''
        else:
            if self.content.endswith(convert_to_pleco_syntax('newline')):
                self.content.rstrip(convert_to_pleco_syntax('newline'))
            return convert_to_pleco_syntax([self.block_command,'block'],self.content)
    
    def load(self,template):
        w=Writer(template=template,character=self.__character)
        self.content=w.text
        return self.write()
    
class Writer():
    def __init__(self,template,character:Character):
        self.__used_template=template
        self.__use_template()
        self.current_header=None
        self.current_content=None
        self.__complete_text=''
        self.__current_line=''
        self.__character=character
        self.get_container()
        
    def __use_template(self, keep_newline:bool=False):
        if self.__used_template.endswith('.chd'):
            template=''
            with open(self.__used_template) as f:
                lines = f.readlines()
                if keep_newline:
                    lines=[line.rstrip('\n') if line!='\n' else '<N>' for line in lines]
                else:
                    lines=[line.rstrip('\n') for line in lines if line!='\n']
                template=''.join(lines)
            self.__used_template=template
            self.template=template
            
        
    def get_container(self):
        # container options: H (header),L (list),T (text),indent (block),right (block),left (block),
        # N (newline), E (end)
        
        if self.__used_template=="":
            pass
        elif self.__used_template!="":
            container,self.__used_template = re.match(r'.*?<(.*?)>(.*)',self.__used_template).groups()
            container_specs = container.split(':')
            if len(container_specs)>1:
                if container.startswith('H'):
                    self.current_header=Header(container=container)
                    self.get_container()
                elif container[0] in ['L','T','I']: # could also be L_LINK, ...
                    self.current_content=Content(container=container,character=self.__character)
                    self.__current_line+=self.current_content.write()
                    self.get_container()
                    
            elif len(container_specs)==1:
                block_commands=['indent','right','left','mark','markline']
                block_command=[c for c in block_commands if container.lower()==c]
                if len(block_command)==1:
                    # write block
                    self.current_block=Block(command=block_command[0],character=self.__character)
                    container,self.__used_template=re.match(r'\{(.*?)\}(.*)',self.__used_template).groups()
                    self.current_block.load(template=container)
                    self.__current_line+=self.current_block.write()
                    self.get_container()
                elif container=='E':
                    # marks the end of a line
                    if self.current_header!=None:
                        self.__complete_text+=self.current_header.write_with_content(self.__current_line)
                    else:
                        self.__complete_text+=self.__current_line
                    self.__current_line=''
                    self.current_content=None
                    self.current_content=None
                    self.current_block=None
                    self.get_container()
                elif container.upper()=='N':
                    # newline
                    if container=='N': self.__current_line+=convert_to_pleco_syntax('newline')
                    if container=='n': self.__current_line+='\n'
                    self.get_container()
                elif container=='TAB':
                    self.__current_line+=convert_to_pleco_syntax('tab')
                    self.get_container()
                else:
                    if not re.search(r'\w', container):
                        # Any other non word characters in <...> can be written down like this
                        self.__current_line+=container
                    self.get_container()
                    
    @property    
    def text(self):
        return self.__complete_text
    
    def add_uniq(self):
        uniq = [e if e!=None else "" for e in self.__character.uniq]
        simple, traditional, pronunciation = uniq
        traditional = convert_to_pleco_syntax('bracket',traditional)
        pronunciation = encode_pinyin(pronunciation)
        uniqstring=f'{simple}{traditional}\t{pronunciation}\t'
        self.__complete_text=uniqstring+self.__complete_text
    
    def link_pronunciations(self):
        self.__complete_text = link_pronunciations(text=self.__complete_text)
    
    def print(self):
        print(self.__complete_text)
        
class Loader():
    dtype_map={'L':list,'T':str,'I':int,'list':list,'str':str,'int':int}
    
    def __init__(self,template):
        self.template=template
        self.__use_template()
        self.__analyze_template()
        self.__additional_categories={'images':dict,'image_urls':list}
        
    @property
    def categories(self):
        dtype_lookup = {
            "list": list,
            "str": str,
            "int": int,
            "dict": dict,
        }
        categories={'simple':str,'traditional':str,'pronunciation':str}
        categories.update({k:v['type'] for k,v in self.helper.items()})
        categories.update(self.__additional_categories)
        categories={k:[s for s,dtype in dtype_lookup.items() if dtype==v][0] for k,v in categories.items()}
        return categories
        
    def __use_template(self):
        if self.template.endswith('.chd'):
            template=''
            with open(self.template) as f:
                lines = f.readlines()
                lines=[line.replace('\t','').rstrip('\n') for line in lines if line!='\n']
                template=''.join(lines)
            self.template=template
    
    def __analyze_template(self):
        helper={}
        for m in re.findall(r'<H(?:(?!<H).)*<E>',self.template):
            with_header = re.findall(r'<H(?:(?!<H|\{|\}).)*<E>',m)
            if with_header != []:
                
                header,content = re.search(r'<H:.*?:(.*?)>(.*)',m).groups()
                content = re.findall(r'<(.):(.*?):(.*?)>',content)
                for c in content:
                    kind=c[0]
                    dtype=self.dtype_map[kind]
                    specs=c[1]
                    content_name = c[2]
                    helper[content_name]={'type':dtype,'header':header,'specs':specs}
            else:
                without_header = re.findall(r'<(?:(?!\{|\}).)*><E>',m)
                for content in without_header:
                    c = re.search(r'<(.*?):(.*?):(.*?)>.*',content).groups()
                    kind=c[0]
                    kind=re.match(r'(.).*',kind).group(1)
                    dtype=self.dtype_map[kind]
                    specs=c[1]
                    content_name = c[2]
                    helper[content_name]={'type':dtype,'header':None,'specs':specs}
        self.helper = helper
    
    def __line_content(self,line,name):
        dtype=self.helper[name]['type']
        specs=self.helper[name]['specs']
        if dtype==int:
            return int(re.match(r'.*(\d+).*',line).group(1))
        elif dtype==str:
            return line
        elif dtype==list:
            specs=re.match(r'\[(.*)\]',specs).group(1)
            sep=get_sep(specs.split('|')[0])
            newline=get_line(specs.split('|')[1])
            if sep!=None:
                sep=convert_to_pleco_syntax(get_sep(sep))
                return [e.strip(' ') for e in line.split(sep) if e!='']
            elif newline == 'newline':
                line=line.split(convert_to_pleco_syntax('newline'))
                line=[self.__remove_syntax(l) for l in line]
                return [l for l in line if l!='']
            else:
                line=self.__remove_syntax(line)
                return [line]
    
    def character(self,content:str):
        symbols,pronunciation,content=content.split('\t')
        symbols=self.__get_symbols(symbols=symbols)
        
        rest_text=content
        rest_header=''
        count_header={v['header']:0 for v in self.helper.values() if v['header']!=None}
        result={'simple':symbols[0],'traditional':symbols[1],'pronunciation':pronunciation}
        
        for k,v in self.helper.items():
            h=v['header']
            if h!=None:
                newline=convert_to_pleco_syntax('newline')
                lines=re.findall(rf'{h}[{pleco_char}]*.*?[{newline}]',content)
                for line in lines:
                    rest_text=rest_text[rest_text.find(line)+len(line):]
                    line = self.__remove_syntax(line)
                    line = line[len(h):]
                    result[k]=self.__line_content(line,name=k)
                    count_header[h]+=1
            else:
                rest_header=k
        result[rest_header]=self.__line_content(rest_text,rest_header)
        self.__resolve_multiple_header(count_header,result)
        return result

    def __resolve_multiple_header(self,counts,result):
    
        def change_strokes(result,multiple):
            multiple_vals = {k:v for k,v in result.items() if k in multiple}
            strokes=multiple_vals['strokes']
            strokes_count=str(multiple_vals['strokes_count'])
            strokes=strokes.replace(f'({strokes_count})','').strip(' ')
            result['strokes']=strokes
            return result
        changer = {('strokes_count','strokes'):change_strokes}
        
        multiple_header=[h for h,v in counts.items() if v>1]
        multiple_keys={k:v['header'] for k,v in self.helper.items() if v['header'] in multiple_header}
        multiple_header={h:[k for k,v in multiple_keys.items() if v==h] for h in multiple_header}
        
        for keys in multiple_header.values():
            change_func=[f for c_keys,f in changer.items() if sorted(list(c_keys))==sorted(keys)]
            if len(change_func)==1:
                change_func=change_func[0]
                return change_func(result=result,multiple=keys)
            else:
                return result
    
    def __remove_syntax(self,text):
        text = re.sub(rf'[{pleco_char}]+','',text)
        rm = ['1A0A','A0P','1A0P','AA10','AA00']
        for r in rm:
            text=text.replace(r,'')
        return text.strip(' ')
    
    def __get_symbols(self,symbols):
        # should return a list (len=2) 
        # of simplified and traditional character (if there)
        symbols=re.findall('([\u4e00-\u9fff]+)',symbols)
        if len(symbols)==1:
            # if only one chataczer -> will always be seen as simplified form
            symbols+=['']
        elif len(symbols)==0:
            symbols=['','']
        elif len(symbols)>2:
            print('WARNING: More than one symbol representation',symbols)
        return symbols
