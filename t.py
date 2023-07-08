import os

if os.name == 'nt':
    import win32api

    win32api.LoadLibrary('LocationRotation')

import fastdds
import LocationRotation

print("Succeeded")
