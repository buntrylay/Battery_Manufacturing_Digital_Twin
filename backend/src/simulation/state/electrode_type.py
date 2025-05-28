from dataclasses import dataclass


@dataclass
class ElectrodeType:
    Anode: str = "Anode"
    Cathode: str = "Cathode"