from datetime import datetime, timedelta
import time
import json

# --- Configuration ---
class MixingConfiguration:
    def __init__(self, ratios: dict, volume_liters: float):
        self.ratios = ratios
        self.volume_liters = volume_liters

# --- State ---
class Slurry:
    def __init__(self, solvent: str):
        self.AM = 0.0
        self.CA = 0.0
        self.PVDF = 0.0
        self.solvent = solvent
        self._solvent_volume = 0.0
        self.viscosity = 0.0
        self.density = 0.0
        self.yield_stress = 0.0
        self.timestamp = None

    def add(self, component: str, amount: float):
        if component == self.solvent:
            self._solvent_volume += amount
        else:
            setattr(self, component, getattr(self, component) + amount)

    def as_dict(self):
        return {
            "TimeStamp": self.timestamp.isoformat() if self.timestamp else None,
            "AM": self.AM,
            "CA": self.CA,
            "PVDF": self.PVDF,
            self.solvent: self._solvent_volume,
            "viscosity": self.viscosity,
            "density": self.density,
            "yield_stress": self.yield_stress
        }

    def update_properties(self, viscosity: float, density: float, yield_stress: float):
        self.viscosity = viscosity
        self.density = density
        self.yield_stress = yield_stress

# --- Calculator ---
class SlurryPropertyCalculator:
    def calculate_properties(self, data):
        AM = data.get("AM", 0)
        CA = data.get("CA", 0)
        PVDF = data.get("PVDF", 0)
        solvent = next(k for k in data if k not in ["AM", "CA", "PVDF", "TimeStamp"])
        solvent_volume = data.get(solvent, 0)
        
        total_solids = AM + CA + PVDF
        total_volume = total_solids + solvent_volume

        density = (AM * 2.26 + CA * 1.8 + PVDF * 1.17 + solvent_volume * 1.0) / total_volume if total_volume else 0
        viscosity = 0.85 * AM + 2.2 * PVDF + 0.3 * CA - 0.4 * solvent_volume
        yield_stress = 0.1 * viscosity

        return {
            "viscosity": round(viscosity, 2),
            "density": round(density, 4),
            "yield_stress": round(yield_stress, 2)
        }

# --- Simulation Process ---
class MixingProcess:
    def __init__(self, config: MixingConfiguration, calculator: SlurryPropertyCalculator, slurry: Slurry):
        self.config = config
        self.calculator = calculator
        self.slurry = slurry
        self.total_time = 0
        self.start_time = datetime.now()

    def run(self, step_percent=0.02, pause_sec=0.1):
        for component in ["PVDF", "CA", "AM"]:
            self._mix_component(component, step_percent, pause_sec)
        self._finalize()

    def _mix_component(self, component, step_percent, pause_sec):
        total = self.config.volume_liters * self.config.ratios[component]
        step_volume = step_percent * total
        steps = int(1 / step_percent)

        for _ in range(steps):
            self.total_time += pause_sec
            self.slurry.add(component, step_volume)
            self.slurry.timestamp = self.start_time + timedelta(seconds=self.total_time)

            data = self.slurry.as_dict()
            properties = self.calculator.calculate_properties(data)
            self.slurry.update_properties(**properties)

            print(json.dumps(self.slurry.as_dict(), indent=2))
            time.sleep(pause_sec)

    def _finalize(self):
        print("\nFinal Slurry State:")
        print(json.dumps(self.slurry.as_dict(), indent=2))

# --- Main Execution ---
if __name__ == "__main__":
    user_ratios = {"AM": 0.495, "CA": 0.045, "PVDF": 0.05, "H2O": 0.41}
    config = MixingConfiguration(ratios=user_ratios, volume_liters=200)
    slurry = Slurry(solvent="H2O")
    calculator = SlurryPropertyCalculator()
    process = MixingProcess(config, calculator, slurry)
    process.run()
