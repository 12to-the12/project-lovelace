class Config:
    def __init__(self):
        self.temporal_adjustment_ms = 50
        self.temporal_adjustment = self.temporal_adjustment_ms / 1_000
        self.draw_last_pos = True
        self.draw_interpolated = False
        self.draw_time_dilated = True
        self.draw_self = True
        self.desktop_mode = False
        self.readout_interval_ms = 1000  # ms
        self.pingmode = False
        self.single_threaded_io = True

        self.server_address = "lovelace.loganhillyer.me"
        self.snapshot_interval_ms = 20
        self.acc_factor = 1e3
        self.sap = 0.5


config = Config()
