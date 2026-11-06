import pandas as pd


class TestCampaign:
    def __init__(self):
        self.tests = []

    def add_test(self, test):
        self.tests.append(test)

    def get_summary(self):
        results = []

        for test in self.tests:
            specimen = test.specimen
            complete = test.detect_fracture()

            results.append({
                "test_id": specimen.test_id,
                "material": specimen.material,
                "E_GPa": test.youngs_modulus(),
                "yield_MPa": test.yield_strength_02(),
                "uts_MPa": test.ultimate_tensile_strength() if complete else None,
                "fracture_strain": test.elongation_at_fracture() if complete else None,
                "complete": complete
            })

        return pd.DataFrame(results)

    def save_summary(self, output_path="outputs/summary.csv"):
        summary = self.get_summary()
        summary.to_csv(output_path, index=False)
        return summary