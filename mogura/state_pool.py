class StatePool:

    def __init__(self):
        self.id_to_state_dict = {}
        self.active_id = None
        self.active_state = None
        self.new_state = None

    def add_state(self, state):
        self.id_to_state_dict[state.id] = state

    def set_active(self, id):
        self.active_id = id
        self.new_state = self.id_to_state_dict.get(self.active_id, None)

    def screen_tick(self, screen, sec):
        if self.active_state is None: return
        self.active_state.screen_tick(screen, sec)

    def event_tick(self, event, sec):
        if self.active_state != self.new_state:
            if self.active_state is not None:
                self.active_state.on_inactive()
            self.active_state = self.new_state
            if self.active_state is not None:
                self.active_state.on_active()
    
        if self.active_state is None: return
        self.active_state.event_tick(event, sec)
