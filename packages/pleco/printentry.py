from .convert_instructions import plecoformat
from .entry import entry

def list_definitions(definitions,bullet='dot',newline=False):
    if type(definitions)==list:
        if definitions==['']: linestart=''
        else: linestart=plecoformat(bullet)
        if newline:
            liststring=f'{plecoformat("newline")}{plecoformat(bullet)} '.join(definitions)
        else:
            liststring=f' {plecoformat(bullet)} '.join(definitions)
        if bullet=='point':
            content=f'{linestart} '+liststring
        else:
            content=liststring
    elif definitions==None:
        content=''
    else:
        content=definitions
    return content

def definition(aspect: str, color: str, boldness: str, bullet='dot', elements=None, newline=False) -> str:
    
    if elements!=None and not newline:
        result=plecoformat(color,plecoformat(f'{boldness}',f'{aspect} '))+list_definitions(definitions=elements, bullet=bullet)+plecoformat('newline')
    elif elements!=None and newline:
        result=plecoformat(color,plecoformat(f'{boldness}',f'{aspect} '))+plecoformat('newline')+list_definitions(definitions=elements, bullet=bullet)+plecoformat('newline')
    else: result=''
    return result
    

class plecoprinter():
    def __init__(self,entry=None):
        if entry==None:
            # creates entry witch no information at all
            self.__entry=entry()
        else:
            # attributes of entry depend on how dictionary defines characters
            self.__entry=entry

    def translation(self):
        return plecoformat(
            'left',
            definition('ENG','blue','narrowbold','point',self.__entry.english)+
            definition('GER','blue','narrowbold','point',self.__entry.german)+
            definition('MW ','teal','narrowbold','point',self.__entry.measure_word)+
            definition('RAD','teal','narrowbold','point',self.__entry.radical)+
            definition('OPP','green','narrowbold','point',self.__entry.opposite)
            )
    def information(self):
        if self.__entry.dict_entries!=None: 
            dict_entries=[plecoformat('link',de) for de in self.__entry.dict_entries]
        else:
            dict_entries=None
        return plecoformat('grey',plecoformat('bold','INFORMATION'))+plecoformat(
            'indent',
            # definition('STROKES:','grey','bold','dot',f'({self.__entry.strokecount}) {self.__entry.strokeorder}')+
            definition('STROKES:','grey','bold','dot',self.__entry.strokes)+
            definition('CLASSIFIER:','grey','bold','dot',self.__entry.classifier)+
            definition('VARIANTS:','grey','bold','dot',self.__entry.variants)+
            definition('RELATIVES:','grey','bold','dot',self.__entry.relatives)+
            definition('WORDS:','grey','bold','dot',self.__entry.words)+
            definition('DISTINGUISH:','grey','bold','dot',self.__entry.others)+
            definition('DICTIONARY ENTRIES:','grey','bold','dot',dict_entries,newline=True)
        )
    def meaning(self):
        if self.__entry.components!=None:
            components=[c for c in self.__entry.components if len(c) <=5]
            components_explained=[c for c in self.__entry.components if len(c) >5]
            if len(components_explained)>0: comp=list_definitions(components_explained,bullet='point',newline=True)+plecoformat('newline')
            else: comp=''
        else:
            comp=''
            components=self.__entry.components
        return plecoformat('grey',plecoformat('bold','CHARACTER MEANING'))+plecoformat(
            'indent',
            definition('COMPONENTS:','grey','bold','dot',components)+comp+
            definition('MNEOMICS:','grey','bold','point',self.__entry.mneomics)+
            definition('COMPONENT USAGE:','grey','bold','point',self.__entry.usage)+
            definition('ORIGINS:','grey','bold','point',self.__entry.origin)
        ) 

    def ancient_form(self):
        ancientform = ''.join(self.__entry.ancient) if isinstance(self.__entry.ancient,list) else self.__entry.ancient
        ancientform = ancientform if ancientform != None else ""
        return plecoformat('grey',plecoformat('bold','ANCIENT FORM:'))+plecoformat('textbig',f'{ancientform}')

    def links(self):
        links= self.__entry.link if self.__entry.link != None else []
        if len(links) > 0:
            zitoolslinks=[plecoformat('link',link) +plecoformat('newline') for link in links]
            return plecoformat('right',plecoformat('textsmall',''.join(zitoolslinks)))
        else:
            return ""