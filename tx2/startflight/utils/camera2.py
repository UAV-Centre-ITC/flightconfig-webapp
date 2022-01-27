import ptpy
from datetime import datetime

def RunCamera():

    camera = ptpy.PTPy()

    with camera.session():

        capture = camera.initiate_capture()

        while True:
            event = camera.event()
            if event and event.EventCode == 'ObjectAdded':

                handle = event.Parameter[0]

                info = camera.get_object_info(handle)

                # Download all things that are not groups of other things.
                if info.ObjectFormat != 'Association':
                    obj = camera.get_object(handle)
                    print(info.Filename)
                    with open(info.Filename, mode='wb') as f:
                        f.write(obj.Data)


RunCamera()
