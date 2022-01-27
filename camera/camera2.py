import ptpy
from datetime import datetime

camera = ptpy.PTPy()
# now = datetime.now()
# date_time = now.strftime("%Y-%m-%d %H:%M:%S")
# date_time2 = str(now.strftime("%Y%m%dT%H%M%S"))
# print(type(date_time2))
# camera.set_device_prop_value('DateTime', date_time)
# print(camera.get_device_prop_value('DateTime'))

with camera.session():
    device_info = camera.get_device_info()
    # print(device_info)
    # set_device_info = camera.send_object_info()
    # for prop in device_info:
    #     print(prop)

    # print('working?', camera.get_device_prop_value('DateTime'))

    capture = camera.initiate_capture()

    while True:
        event = camera.event()
        if event and event.EventCode == 'ObjectAdded':
            # print('evt', evt)
            # print('evtcode', evt.EventCode)
            # print('parameters', evt.Parameter)
            handle = event.Parameter[0]

            info = camera.get_object_info(handle)
            # print('info', info)
            # print(str(date_time))
            # info.CaptureDate = now
            # info.ModificationDate = now
            # print('info test', info)

            # while True:
            #     event2 = camera.event()
            #     info2 = camera.send_object_info(info)
            #     if event2 and event2.EventCode == 'CaptureComplete':
            #         print('event2', event2)
            #         handle2 = event2.Parameter[0]
            #
            #         info2 = camera.get_device_info(handle2)
            #         print('info copied ', info2)

            # Download all things that are not groups of other things.
            if info.ObjectFormat != 'Association':
                obj = camera.get_object(handle)

                with open(info.Filename, mode='wb') as f:
                    f.write(obj.Data)

    # ids = camera.get_storage_ids()
    # print('ids', ids)

# with camera.session():
#     event = camera.event()
#     print('event', event)
#
#     if event and event.EventCode == 'ObjectAdded':
#         handle = event.Parameter[0]
#         print(handle)

        # handles = camera.get_object_handles(stor_id)
        # print('handles', handles)
        #
        # for handle in handles: #This line is passing handles from images that are already taken, need to get handles from capture (see above) or from specific session
        #     info = camera.get_object_info(handle)
        #     print('info', info)
        #     # Download all things that are not groups of other things.
        #     if info.ObjectFormat != 'Association':
        #         obj = camera.get_object(handle)
        #             # print('obj', obj)
        #         with open(info.Filename, mode='wb') as f:
        #             f.write(obj.Data)
