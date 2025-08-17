import numpy as np

class FormationCyclingPropertyCalculator:
    """
    Calculates properties related to the battery cell formation cycling process which is after the electrolyte filling.
    Important to note that in the first charge it is important that the 
    Formation cycling is the first electrochemical activation of the battery cell. 
    After the cell is sealed and electrolyte is added, it undergoes controlled charge-discharge 
    cycles to form a stable solid electrolyte interphase (SEI) layer on the anode and ensure proper 
    lithium intercalation.
    Coulombic Efficiency (CE) - measures how much electricity to put into the battery during charging adn then how much you can get back out
    when it is being used(ie discharge) - being greater than 95% is really good
    """
    
    def __init__(self, Q_theoretical_Ah: float, k_SEI: float, t50_SEI_formation_s: float):
        """
        Initializes the calculator with cell-specific and SEI model parameters.

        Args:
            Q_theoretical_Ah (float): Theoretical maximum capacity of the cell in Ampere-hours.
            k_SEI (float): SEI layer growth rate constant (1/s).
            t50_SEI_formation_s (float): Time at which 50% of the SEI layer is formed (seconds).
        """
        self.Q_theoretical_Ah = Q_theoretical_Ah
        self.k_SEI = k_SEI
        self.t50_SEI_formation_s = t50_SEI_formation_s