class Slurry:
    def __init__(self, volume):
        self.total_volume = volume
        self.AM = 0
        self.CB = 0
        self.PVDF = 0
        self.NMP = 0

    def add(self, component, amount):
        setattr(self, component, getattr(self, component) + amount)