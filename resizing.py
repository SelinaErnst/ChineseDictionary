
def change_metrics():
    from kivy.utils import platform
    import os
    if platform in ["linux","win"]:
        # my linux: KIVY_METRICS_FONTSCALE: 1, KIVY_METRICS_DENSITY: 1, KIVY_DPI: 96 -> dp(1): 1, sp(1): 1

        # os.environ['KIVY_METRICS_DENSITY'] = '2.625'
        # os.environ['KIVY_DPI'] = '420'
        # os.environ['KIVY_METRICS_FONTSCALE'] = '1.0'
        
        # os.environ['KIVY_METRICS_DENSITY'] = '2.8125'
        # os.environ['KIVY_DPI'] = '450'
        # os.environ['KIVY_METRICS_FONTSCALE'] = '1.15'
        
        # Pixel6: KIVY_METRICS_FONTSCALE: 1.145, KIVY_METRICS_DENSITY: 4.025, KIVY_DPI: 560
        os.environ['KIVY_METRICS_DENSITY'] = '4.025'
        os.environ['KIVY_DPI'] = '560'
        os.environ['KIVY_METRICS_FONTSCALE'] = '1.145'
        
        pass
        
    # os.environ['KIVY_METRICS_FONTSCALE'] = '1.4'
        
def window_size(device=None,orientation=None):
    from kivy.core.window import Window
    from kivy.utils import platform
    if platform in ["linux","win"]:
        if device=='GalaxyS24':
            size=[1080,2114]
        elif device=='Pixel6':
            size=[1449,2891]
        elif device=='TabS6':
            size=[1411,2560]
        elif device=='Laptop':
            size=[2000,1700]
        elif device!=None:
            size=[1700,1500]
        else:
            size=[]
        if orientation in ['portrait','p']:
            Window.size = sorted(size)
        elif orientation in ['landscape','l']:
            Window.size = sorted(size,reverse=True)
        elif len(size)==2 and Window != None:
            Window.size = size
        elif Window != None:
            Window.maximize()
    return Window.size