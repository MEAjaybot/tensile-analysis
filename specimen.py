
from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class Specimen:
    test_id: str
    material: str
    area_mm2: float
    length_mm: float


class TensileTest:
    def __init__(self, specimen):
        self.specimen = specimen
        self.df = pd.read_csv(
            f"data/processed/{specimen.test_id}.csv"
        )

    def calculate_stress_strain(self):
        self.df["stress_MPa"] = (
            self.df["force_N"] / self.specimen.area_mm2
        )

        self.df["strain"] = (
            self.df["displacement_mm"] / self.specimen.length_mm
        )

        return self.df

    def youngs_modulus(self, strain_range=(0.0005, 0.002)):
        mask = self.df["strain"].between(*strain_range)
        subset = self.df.loc[mask]

        if len(subset) < 2:
            return None

        slope, _ = np.polyfit(
            subset["strain"], subset["stress_MPa"], 1
        )

        return slope / 1000

    def ultimate_tensile_strength(self):
        if not self.detect_fracture():
            return None

        return self.df["stress_MPa"].max()

    def elongation_at_fracture(self):
        if not self.detect_fracture():
            return None

        force = self.df["force_N"].to_numpy()
        max_index = np.argmax(force)

        fracture_indices = np.where(
            force[max_index + 1:] <= force[max_index] * 0.5
        )[0]

        if len(fracture_indices) == 0:
            return None

        fracture_index = max_index + 1 + fracture_indices[0]

        return self.df["strain"].iloc[fracture_index] * 100

    def yield_strength_02(self):
        strain = self.df["strain"].to_numpy()
        stress = self.df["stress_MPa"].to_numpy()

        mask = (strain >= 0.0005) & (strain <= 0.002)

        if mask.sum() < 2:
            return None

        E, intercept = np.polyfit(strain[mask], stress[mask], 1)

        offset_stress = E * (strain - 0.002) + intercept
        difference = stress - offset_stress

        for i in range(1, len(strain)):
            if difference[i - 1] >= 0 and difference[i] <= 0:
                x1, x2 = strain[i - 1], strain[i]
                y1, y2 = difference[i - 1], difference[i]

                if y1 == y2:
                    return float(stress[i])

                yield_strain = x1 + (
                    (0 - y1) * (x2 - x1) / (y2 - y1)
                )

                return float(np.interp(
                    yield_strain, strain, stress
                ))

        return None

    def detect_fracture(self, drop_ratio=0.5):
        force = self.df["force_N"].to_numpy()

        if len(force) < 3:
            return False

        max_index = np.argmax(force)
        max_force = force[max_index]

        remaining_force = force[max_index + 1:]

        if len(remaining_force) == 0:
            return False

        return np.any(
            remaining_force <= max_force * drop_ratio
        )
