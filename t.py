import os

if os.name == 'nt':
    import win32api

    win32api.LoadLibrary('FastDDSJsonStr')
    # win32api.LoadLibrary('_fastdds_python.pyd')

import fastdds
import FastDDSJsonStr

print("Succeeded")
