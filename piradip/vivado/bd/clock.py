
class Clock:
    def __init__(self, period):
        self._period = period
        
class DiffClock(Clock):
    def __init__(self, period):
        super().__init__(period)
