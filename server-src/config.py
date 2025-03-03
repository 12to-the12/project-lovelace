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

        # self.server_address = "lovelace.loganhillyer.me"
        # self.server_address = "192.168.4.141"
        self.server_address="192.168.4.141"
        # self.server_address = "172.20.10.9"
        self.snapshot_interval_ms = 20
        self.force_factor = 1e2
        self.sap = 0.8
        self.booster = 1e4
        self.fps = 60  # limiter
        self.max_volume = 1
        self.intro = True
        self.production = False


config = Config()
