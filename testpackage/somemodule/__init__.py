from roompi.modules import RoomPiModule


class SomeModule(RoomPiModule):
    module_name = 'SomeModule'
    requires_thread = True