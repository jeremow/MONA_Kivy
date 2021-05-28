# MONA_Kivy

__MONA__ stands for MONitoring App for MONgolian stations. 

Things to do:
1. In the module `obspy/core/util/misc.py`, you comment the line 390. 
   Else it creates a problem with the stderr between Kivy and Obspy (`f.fileno doesn't exist`).
   
        # sys.__stderr__ = sys.stderr = _reopen_stdio(sys.stderr, 'wb')
   
2. Matplotlib modification to add Kivy more easily and avoid problems with garden.
    1. Add to the virtual environment the two files `backend_kivy.py` and `backend_kivyagg.py` in the folder **venv_mona/Lib/site-packages/matplotlib/backends**.
    2. In the module `matplotlib/rcsetup.py`, Change the list of names of interactive backends adding `'Kivy'` and `'KivyAgg'` (l. 43 of the file)

    ```
        interactive_bk = ['GTK', 'GTKAgg', 'GTKCairo', 'GTK3Agg', 'GTK3Cairo',
                          'MacOSX',
                          'nbAgg',
                          'Qt4Agg', 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo',
                          'TkAgg', 'TkCairo',
                          'WebAgg',
                          'WX', 'WXAgg', 'WXCairo',
                          'Kivy', 'KivyAgg']
    ```
   
    3. Last step is to change the import in the project `matplotlib.use('Kivy')`.