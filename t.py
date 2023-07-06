import os

if os.name == 'nt':
    import win32api

    win32api.LoadLibrary('TestDemo')

import fastdds

t = fastdds.DomainParticipantFactory.get_instance()
print("Succeeded")
