# from .convert_instructions import plecoformat

# def list_definitions(definitions,bullet='dot',newline=False):
#     bullet_point=plecoformat(bullet) if bullet not in ["",None] else ""
#     if type(definitions)==list:
#         if definitions==['']: linestart=''
#         else: linestart=bullet_point
#         if newline:
#             liststring=f'{plecoformat("newline")}{bullet_point} '.join(definitions)
#         else:
#             liststring=f' {bullet_point} '.join(definitions)
#         if bullet=='point':
#             content=f'{linestart} '+liststring
#         else:
#             content=liststring
#     elif definitions==None:
#         content=''
#     else:
#         content=definitions
#     return content

# def definition(aspect: str, color: str, boldness: str, bullet='dot', elements=None, newline=False) -> str:
    
#     if elements!=None and not newline:
#         result=plecoformat(
#             color,
#             plecoformat(
#                 f'{boldness}',
#                 f'{aspect} ')
#             )+list_definitions(definitions=elements, bullet=bullet)+plecoformat('newline')
#     elif elements!=None and newline:
#         result=plecoformat(color,plecoformat(f'{boldness}',f'{aspect} '))+plecoformat('newline')+list_definitions(definitions=elements, bullet=bullet)+plecoformat('newline')
#     else: result=''
#     return result

# def link_to_string(match):
#     naked_string = match.group().lstrip('[').rstrip(']')
#     # naked_string=decode_pinyin(naked_string)
#     linked_string = plecoformat('link',naked_string)
#     return f'[{linked_string}]'

# def pyinyin_to_string(match):
#     naked_string = match.group().lstrip('[').rstrip(']')
#     pinyin_string = decode_pinyin(naked_string)
#     # print(naked_string,pinyin_string)
#     return f'[{pinyin_string}]'

# def link_pronunciations(plecostring):
#     # pattern = rf"\[(?:(?![{chinese_char}])[\S]+)\]"
#     # pattern = r"\[(?:(?![\u4e00-\u9fff])[\S]+)\]"
#     pattern = rf'\[([{not_chinese_char}]+)\]'
#     return re.sub(pattern,link_to_string,plecostring)

# def convert_pronunciations(plecostring):
#     pattern = rf'\[([{not_chinese_char}]+)\]'
#     # pattern = rf'\[(?![{chinese_char}]+)(.+?)\]'
#     return re.sub(pattern,pyinyin_to_string,plecostring)

# class plecoprinter():
#     def __init__(self,entry=None):
#         if entry==None:
#             # creates entry witch no information at all
#             self.__entry=entry()
#         else:
#             # attributes of entry depend on how dictionary defines characters
#             self.__entry=entry

#     def translation(self):
#         categories=['english','german','measure_word','radical','opposite']
#         n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
#         if n_categories < 1: return ''
#         return plecoformat(
#             'left',
#             definition('ENG','blue','narrowbold','point',self.__entry.english)+
#             definition('GER','blue','narrowbold','point',self.__entry.german)+
#             definition('MW ','teal','narrowbold','point',self.__entry.measure_word)+
#             definition('RAD','teal','narrowbold','point',self.__entry.radical)+
#             definition('OPP','green','narrowbold','point',self.__entry.opposite)
#             )
#     def information(self):
#         categories=['strokes','classifier','variants','relatives','words','others','dict_entries']
#         n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
#         if n_categories < 1: return ''
        
#         if self.__entry.dict_entries!=None: 
#             dict_entries=[plecoformat('link',de) for de in self.__entry.dict_entries]
#         else:
#             dict_entries=None
#         title=plecoformat('grey',plecoformat('bold','INFORMATION')) 
#         content=plecoformat(
#             'indent',
#             definition('CLASSIFIER:','grey','narrowbold','dot',self.__entry.classifier)+
#             definition('VARIANTS:','grey','narrowbold','dot',self.__entry.variants)+
#             definition('DISTINGUISH:','grey','narrowbold','dot',self.__entry.others)+
#             definition('DICTIONARY ENTRIES:','grey','narrowbold','dot',dict_entries,newline=True)
#         )
#         return title+content
    
#     def words_and_characters(self):
#         categories=['relatives','words']
#         n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
#         if n_categories < 1: return ''
#         title=plecoformat('grey',plecoformat('bold','OCCURENCES')) 
#         content=plecoformat(
#             'indent',
#             definition('RELATIVES:','grey','narrowbold','dot',self.__entry.relatives)+
#             definition('WORDS:','grey','narrowbold','dot',self.__entry.words)
#             )   
#         return title+content
    
#     def meaning(self):
#         categories=['components','mnemonics','usage','origin']
#         n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
#         if n_categories < 1: return ''
        
#         if self.__entry.components!=None:
#             components=[c for c in self.__entry.components if len(c) <=5]
#             components_explained=[c for c in self.__entry.components if len(c) >5]
#             if len(components_explained)>0: comp=list_definitions(components_explained,bullet='point',newline=True)+plecoformat('newline')
#             else: comp=''
#         else:
#             comp=''
#             components=self.__entry.components
            
#         title=plecoformat('grey',plecoformat('bold','CHARACTER'))
#         ancient_form = ''.join(self.__entry.ancient) if isinstance(self.__entry.ancient,list) else self.__entry.ancient
#         ancient_form = ancient_form if ancient_form != None else ""
#         ancient_form = plecoformat('textbig',f'{ancient_form}')
#         content=plecoformat(
#             'indent',
#             definition('STROKES:','grey','narrowbold','dot',self.__entry.strokes)+
#             definition('COMPONENTS:','grey','narrowbold','dot',components)+comp+
#             definition('MNEMONICS:','grey','narrowbold','point',self.__entry.mnemonics)+
#             definition('MEANING AS COMPONENT:','grey','narrowbold','point',self.__entry.usage)+
#             definition('ORIGINS:','grey','narrowbold','point',self.__entry.origin)+
#             definition('ANCIENT FORM:','grey','narrowbold',None,ancient_form)
#         ) 
#         return title+content

#     # def ancient_form(self):
#     #     categories=['ancient']
#     #     n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
#     #     if n_categories < 1: return ''
        
#     #     title=plecoformat('grey',plecoformat('bold','ANCIENT FORM:'))
#     #     content=plecoformat('textbig',f'{ancientform}')+plecoformat('newline')
#     #     return title+content

#     def links(self):
#         categories=['link']
#         n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
#         if n_categories < 1: return ''
        
#         links= self.__entry.link if self.__entry.link != None else []
#         if len(links) > 0:
#             zitoolslinks=[plecoformat('link',link) +plecoformat('newline') for link in links]
#             return plecoformat('right',plecoformat('textsmall',''.join(zitoolslinks)))
#         else:
#             return ""