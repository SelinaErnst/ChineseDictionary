
def change_metrics():
    from kivy.utils import platform
    import os
    if platform in ["linux","win"]:
        # my linux: KIVY_METRICS_FONTSCALE: 1, KIVY_METRICS_DENSITY: 1, KIVY_DPI: 96 -> dp(1): 1, sp(1): 1

        # os.environ['KIVY_METRICS_DENSITY'] = '2.625'
        # os.environ['KIVY_DPI'] = '420'
        # os.environ['KIVY_METRICS_FONTSCALE'] = '1.0'
        
        os.environ['KIVY_METRICS_DENSITY'] = '2.8125'
        # os.environ['KIVY_DPI'] = '450'
        # os.environ['KIVY_METRICS_FONTSCALE'] = '1.15'
        pass
        
    # os.environ['KIVY_METRICS_FONTSCALE'] = '1.4'
    os.environ['KIVY_METRICS_FONTSCALE'] = '1.48'
        
def window_size(device=None,orientation=None):
    from kivy.core.window import Window
    from kivy.utils import platform
    if platform in ["linux","win"]:
        if device=='GalaxyS24':
            size=[1080,2114]
        elif device=='TabS6':
            size=[1411,2560]
        elif device!=None:
            size=[1700,1500]
        else:
            Window.maximize()
        
        if orientation in ['portrait','p'] or orientation==None:
            Window.size = sorted(size)
        elif orientation in ['landscape','l']:
            Window.size = sorted(size,reverse=True)
        else:
            Window.maximize()