import re
from .possible_instructions import possible_instructions

def frame_text(start:str,context:str,end:str):
    """
    intended to either give out a conjugated string 
    when all given parameters are strings.
    When one parameter is NONE -> return empty string
    """
    try:
        # simple enough, but does not work with None types -> Type Error
        result=start+context+end
    except TypeError as err:
        result=''
    return result

def format_frame(possible_instr:dict):
    """
    in possible_instructions we have format_start and format_end 
    instructions. These are always used together. 
    Here a dictionary (frame) is created that throws them together
    under a common name (key).
    """
    all_valid=list(possible_instr.keys())
    start=[i for i in all_valid if i.endswith('start')]
    end=[i for i in all_valid if i.endswith('end')]
    frame={
        s.rstrip('start').rstrip('_'):{'start':possible_instr[s],'end':possible_instr[e]}
        for s,e in zip(start,end) if s.rstrip('start')==e.rstrip('end')
    }
    return frame

def plecoformat(
    instr:str,
    text=None,
    possible_instr:dict=possible_instructions,
    color:str=None,
    block_pos:str=None) -> str:
    """     
    Function to convert simple instructions into PLECO format. 
    Pleco uses special unicode characters (PUA: Private Use Area) to format their dictionaries. 
    The correspondent format is decided by possible (default: possible_instructions)
    ## Parameters
    - **instr** : _str_  
        Instructions for format can be: newline, tab, block, point, dot   
    - **text** : _any_ | _default=None_  
        format this text (frame the text with start and end of format)  
    - **possible_instr** : _dict_ | _default=possible_instructions_  
        dictionary of instructions and their correspondent format string  
    - **color** : _str_ | _default=None_  
        text color, only required if instr=color, available options: blue, color_blue, etc  
    - **block_pos** : _str_ | _default=None_  
        block position, only required if instr=block, available options: left, block_left, etc  
    ## Returns
    - _str_  
        character string of PLECO format characters
    
    """
    # list of valid instructions
    all_valid=list(possible_instr.keys())
    # create frame format instructions using valid instructions 
    # that end with _start/_end 
    frame=format_frame(possible_instr)
    # in case of color or block (frame) format: what are the options for color / block position
    color_options=[c.replace('color_','') for c in all_valid if c.startswith('color_') and not any(re.findall(r'start|end',c))]
    block_options=[c.replace('block_','') for c in all_valid if c.startswith('block_') and not any(re.findall(r'start|end',c))]
    try:
        # in case instr includes consits of frame format instr (color) and specifics (blue) -> color_blue or block_left
        # instr is then replaced by frame format, and variables for specifics are redefined (instr is prioritized)
        if any(re.findall(r'|'.join(color_options),instr)):
            color='color_'+instr.replace('color_','')
            instr='color'      
        elif any(re.findall(r'|'.join(block_options),instr)):
            block_pos='block_'+instr.replace('block_','')
            instr='block'       
        # frame format instr are used to format text
        if instr in frame.keys():
            # find correspondent PLECO formats
            frame_start,frame_end=frame[instr]['start'],frame[instr]['end']
            # frame text (in between start and end)
            if instr=='color':
                color='color_'+ color.replace('color_','')
                # return complete PLECO color format when text is given
                if text!=None: 
                    color=possible_instr[color]
                    text=color+text
                    sym=frame_text(frame_start,text,frame_end)
                # When text is missing, only return PLECO color (usually 4 characters)
                else: sym=possible_instr[color]
            elif instr=='block':
                block_pos='block_'+ block_pos.replace('block_','')
                # return complete PLECO block format when text is given
                if text!=None: 
                    block_pos=possible_instr[block_pos]
                    text=block_pos+text
                    sym=frame_text(frame_start,text,frame_end)
                # When text is missing, only return PLECO block position (usually 4 characters)
                else: sym=possible_instr[block_pos]
            else:
                sym=frame_text(frame_start,text,frame_end)
        
        # non-frame format instr are (simply) converted to PLECO format 
        else:
            sym=possible_instr[instr]
        return sym
    
    except KeyError as err:
        if instr=='I':
            print('These are all the valid instructions:\n'+'\n'.join(all_valid))
        else:
            print(f'Error: {err} is not a valid instruction. \nTo get a list of all instructions use "I" as input.')
    except AttributeError as err:
        if instr=='color' and color==None:
            # color.replace does not work
            print('Error: A color has to be selected. Possible options are:',', '.join(color_options))
        elif instr=='block' and block_pos==None:
            print('Error: A block_pos has to be selected. Possible options are:',', '.join(block_options))
