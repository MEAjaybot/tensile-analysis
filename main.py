import os
import pandas as pd

from specimen import Specimen, TensileTest
from campaign import TestCampaign


os.makedirs("outputs", exist_ok=True)

specimens_df = pd.read_csv("data/specimens.csv")

campaign = TestCampaign()

for _, row in specimens_df.iterrows():
    specimen = Specimen(
        test_id=row["test_id"],
        material=row["material"],
        area_mm2=row["area_mm2"],
        length_mm=row["gauge_length_mm"]
    )

    test = TensileTest(specimen)

    df = test.calculate_stress_strain()
    df.to_csv(f"outputs/{specimen.test_id}.csv", index=False)

    campaign.add_test(test)

summary_df = campaign.save_summary()

print(summary_df)
print("\nSummary saved to outputs/summary.csv")