import os, json, random
from datetime import datetime, timedelta
import simpy

from simulation.sensor.SlurryPropertyCalculator import SlurryPropertyCalculator
from simulation.battery_model.Slurry import Slurry


class MixingSimPy:
    """
    SimPy-based stand-alone mixer that mimics MixingMachine JSON outputs.
    Keeps the existing Slurry & SlurryPropertyCalculator usage so results match.
    """
    # --------------------------------------------------------------------------
    # THREAD VERSION (previous): constructor gist
    # --------------------------------------------------------------------------
    # class MixingMachine(BaseMachine):
    #     def __init__(self, id, electrode_type, slurry: Slurry, ratios: dict):
    #         super().__init__(id)
    #         self.electrode_type = electrode_type
    #         self.slurry = slurry
    #         self.ratios = ratios
    #         self.start_time = datetime.now()
    #         self.total_time = 0.0
    #         self.lock = threading.Lock()
    #         self.shutdown_event = threading.Event()
    #         # densities/weights per electrode + calculator
    #         if self.electrode_type == "Anode":
    #             self.RHO_values = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "H2O": 1.0}
    #             self.WEIGHTS_values = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
    #             self.slurry.add("H2O", 200 * self.ratios["H2O"])
    #         else:
    #             self.RHO_values = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "NMP": 1.03}
    #             self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}
    #             self.slurry.add("NMP", 200 * self.ratios["NMP"])
    #         self.calc = SlurryPropertyCalculator(self.RHO_values, self.WEIGHTS_values)
    #         self.output_dir = os.path.join(os.getcwd(), "mixing_output")
    #         os.makedirs(self.output_dir, exist_ok=True)
    # --------------------------------------------------------------------------

    def __init__(
        self,
        machine_id: str,
        electrode_type: str,
        slurry: Slurry,
        ratios: dict,
        volume_l: float = 200.0,
        step_percent: float = 0.02,
        tick_sim_s: float = 0.1,
        seed: int = 42,
    ):
        self.id = machine_id
        self.electrode_type = electrode_type
        self.slurry = slurry
        self.ratios = ratios
        self.volume = volume_l
        self.step_percent = step_percent
        self.tick = tick_sim_s
        self.start_datetime = datetime.now()
        random.seed(seed)

        # Output directory consistent with thread version
        self.output_dir = os.path.join(os.getcwd(), "mixing_output")
        os.makedirs(self.output_dir, exist_ok=True)

        # Electrode-specific constants mirroring your MixingMachine
        if self.electrode_type == "Anode":
            self.RHO_values = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "H2O": 1.0}
            self.WEIGHTS_values = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
            # Solvent added up-front in your current flow
            self.slurry.add("H2O", self.volume * self.ratios["H2O"])
            self.solvent_key = "H2O"
        else:
            self.RHO_values = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "NMP": 1.03}
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}
            self.slurry.add("NMP", self.volume * self.ratios["NMP"])
            self.solvent_key = "NMP"

        self.calc = SlurryPropertyCalculator(self.RHO_values, self.WEIGHTS_values)
        self.env = simpy.Environment()

        # throttling snapshot writes
        self._last_saved_result = None
        self._last_saved_wall = datetime.now()

 # ---------- formatting & saving (shape aligned with MixingMachine) ----------

    # --------------------------------------------------------------------------
    # THREAD VERSION (previous): formatting helper (wall-clock based)
    # --------------------------------------------------------------------------
    # def _format_result(self):
    #     ts = (self.start_time + timedelta(seconds=self.total_time)).isoformat()
    #     base = {
    #         "TimeStamp": ts,
    #         "Duration": round(self.total_time, 5),
    #         "Machine ID": self.id,
    #         "Process": "Mixing",
    #         "Electrode Type": self.electrode_type,
    #     }
    #     comp = {
    #         "AM": round(self.slurry.AM, 3),
    #         "CA": round(self.slurry.CA, 3),
    #         "PVDF": round(self.slurry.PVDF, 3),
    #         self.slurry.solvent: round(getattr(self.slurry, self.slurry.solvent), 3),
    #     }
    #     props = {
    #         "Density": round(self.calc.calculate_density(self.slurry), 4),
    #         "Viscosity": round(self.calc.calculate_viscosity(self.slurry), 2),
    #         "YieldStress": round(self.calc.calculate_yield_stress(self.slurry), 2),
    #     }
    #     base.update(comp)
    #     base.update(props)
    #     return base
    # --------------------------------------------------------------------------

    # ---------- formatting & saving (shape aligned with MixingMachine) ----------
    def _format_result(self, sim_t: float, is_final: bool = False):
        base = {
            "TimeStamp": (self.start_datetime + timedelta(seconds=sim_t)).isoformat(),
            "Duration": round(sim_t, 5),
            "Machine ID": self.id,
            "Process": "Mixing",
            "Electrode Type": self.electrode_type,
        }
        composition = {
            "AM": round(getattr(self.slurry, "AM", 0.0), 3),
            "CA": round(getattr(self.slurry, "CA", 0.0), 3),
            "PVDF": round(getattr(self.slurry, "PVDF", 0.0), 3),
            f"{self.slurry.solvent}": round(getattr(self.slurry, self.slurry.solvent), 3),
        }
        properties = {
            "Density": round(self.calc.calculate_density(self.slurry), 4),
            "Viscosity": round(self.calc.calculate_viscosity(self.slurry), 2),
            "YieldStress": round(self.calc.calculate_yield_stress(self.slurry), 2),
        }
        if is_final:
            base["Final Composition"] = composition
            base["Final Properties"] = properties
        else:
            base.update(composition)
            base.update(properties)
        return base

    def _write_json(self, data: dict, filename: str):
        # Use the timestamp from data (keeps parity with thread version)
        ts = data["TimeStamp"].replace(":", "-").replace(".", "-")
        path = os.path.join(self.output_dir, f"{self.id}_{ts}_{filename}")
        if os.path.exists(path):
            return  # skip dup
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return data

# ---------- the mixing process ----------

    # --------------------------------------------------------------------------
    # THREAD VERSION (previous): step loop with sleep + lock
    # --------------------------------------------------------------------------
    # def _mix_component(self, component, step_percent=0.02, pause_sec=0.1):
    #     total_volume = self.total_volume * self.ratios[component]
    #     step_vol = max(total_volume * step_percent, 1e-9)
    #     added = 0.0
    #     while added < total_volume and not self.shutdown_event.is_set():
    #         time.sleep(pause_sec)                # wall-clock wait
    #         with self.lock:                      # guard shared state
    #             self.total_time += pause_sec     # wall clock accumulator
    #             self.slurry.add(component, min(step_vol, total_volume - added))
    #             result = self._format_result()
    #             if self._should_save(result):    # throttled snapshot
    #                 self._write_json(result, f"result_at_{round(self.total_time)}s.json")
    #                 try:
    #                     from server.main import thread_broadcast
    #                     thread_broadcast(f"Machine {self.id} {component} progress @ {round(self.total_time,1)}s")
    #                 except Exception:
    #                     pass
    #         added += step_vol
    # --------------------------------------------------------------------------

    # ---------- the mixing process ----------
    def _mix_component(self, component: str):
        total_volume = self.volume * self.ratios[component]
        step_vol = self.step_percent * total_volume
        added = 0.0
        while added < total_volume:
            # advance simulated time
            yield self.env.timeout(self.tick)
            # add step
            self.slurry.add(component, min(step_vol, total_volume - added))
            added += step_vol

            # periodic snapshot (avoid spamming identical blobs)
            sim_t = float(self.env.now)
            result = self._format_result(sim_t)
            now_wall = datetime.now()
            if (self._last_saved_result != result) and (
                (now_wall - self._last_saved_wall).total_seconds() >= 0.1
            ):
                self._write_json(result, f"result_at_{round(sim_t)}s.json")
                self._last_saved_result = result
                self._last_saved_wall = now_wall
                try:
                    # optional: broadcast to your existing WS if present
                    from server.main import thread_broadcast
                    thread_broadcast(f"SimPy[{self.id}] progress {component} @ {round(sim_t,1)}s")
                except Exception:
                    pass

# --------------------------------------------------------------------------
    # THREAD VERSION (previous): top-level run()
    # --------------------------------------------------------------------------
    # def run(self, step_percent=0.02, pause_sec=0.1):
    #     if self.is_on:
    #         from server.main import thread_broadcast
    #         thread_broadcast(f"Machine {self.id} is already running.")
    #         for comp in ["PVDF", "CA", "AM"]:
    #             self._mix_component(comp, step_percent, pause_sec)
    #         self._save_final_results()
    #         thread_broadcast(f"Machine {self.id} mixing completed.")
    # --------------------------------------------------------------------------

    def _run_all(self):
        # Order matches your current machine: PVDF → CA → AM (solvent already preloaded)
        for comp in ["PVDF", "CA", "AM"]:
            yield from self._mix_component(comp)

        # final snapshot
        sim_t = float(self.env.now)
        final_result = self._format_result(sim_t, is_final=True)
        self._write_json(final_result, "final.json")

        # keep downstream parity
        props = final_result.get("Final Properties", {})
        if hasattr(self.slurry, "update_properties"):
            self.slurry.update_properties(
                props.get("Viscosity", 0.0),
                props.get("Density", 0.0),
                props.get("YieldStress", 0.0),
            )

    # public API
    def run(self):
        try:
            from server.main import thread_broadcast
            thread_broadcast(f"SimPy[{self.id}] mixing started.")
        except Exception:
            pass

        self.env.process(self._run_all())
        self.env.run()

        try:
            from server.main import thread_broadcast
            thread_broadcast(f"SimPy[{self.id}] mixing completed.")
        except Exception:
            pass
