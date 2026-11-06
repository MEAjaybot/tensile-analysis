
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Project folders
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

# Read specimen information and calculated properties
specimens = pd.read_csv("data/specimens.csv")
results = pd.read_csv(OUTPUT_DIR / "summary.csv")

if "material" in results.columns:
    results = results.drop(columns=["material"])

# Combine material information with calculated properties
summary = specimens.merge(results, on="test_id", how="left")


print(summary.columns.tolist())


def find_yield_point(df):
    """Find the 0.2% offset yield point on a stress-strain curve."""

    strain = df["strain"].to_numpy()
    stress = df["stress_MPa"].to_numpy()

    # Fit the initial elastic region
    mask = (strain >= 0.0005) & (strain <= 0.002)

    if mask.sum() < 2:
        return None

    E, intercept = np.polyfit(strain[mask], stress[mask], 1)

    # Calculate 0.2% offset line
    offset_stress = E * (strain - 0.002) + intercept

    difference = stress - offset_stress

    # Find intersection
    for i in range(1, len(strain)):
        if difference[i - 1] >= 0 and difference[i] <= 0:

            x1, x2 = strain[i - 1], strain[i]
            y1, y2 = difference[i - 1], difference[i]

            if y1 == y2:
                return strain[i], stress[i]

            yield_strain = x1 - y1 * (x2 - x1) / (y2 - y1)

            yield_stress = np.interp(
                yield_strain,
                strain,
                stress
            )

            return yield_strain, yield_stress

    return None


# Get unique materials
materials = summary["material"].dropna().unique()

# --------------------------------------------------
# 1. STRESS-STRAIN CURVES FOR EACH MATERIAL
# --------------------------------------------------

for material in materials:

    plt.figure(figsize=(11, 7))

    material_data = summary[summary["material"] == material]

    first_yield_label = True
    first_uts_label = True

    for _, row in material_data.iterrows():

        test_id = row["test_id"]

        # Read processed curve saved by main.py
        file_path = OUTPUT_DIR / f"{test_id}.csv"

        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        df = pd.read_csv(file_path)

        if not {"strain", "stress_MPa"}.issubset(df.columns):
            print(f"Missing stress/strain columns: {test_id}")
            continue

        df = df.dropna(subset=["strain", "stress_MPa"])

        if df.empty:
            continue

        # Plot stress-strain curve
        plt.plot(
            df["strain"],
            df["stress_MPa"],
            label=test_id,
            linewidth=1.5
        )

        # Yield strength marker
        yield_point = find_yield_point(df)

        if yield_point is not None:

            yield_strain, yield_stress = yield_point

            plt.scatter(
                yield_strain,
                yield_stress,
                marker="o",
                s=55,
                label="Yield strength" if first_yield_label else None,
                zorder=3
            )

            first_yield_label = False

        # UTS marker: only show if UTS was calculated
        uts = pd.to_numeric(
            pd.Series([row.get("uts_MPa")]),
            errors="coerce"
        ).iloc[0]

        if pd.notna(uts):

            max_index = df["stress_MPa"].idxmax()

            plt.scatter(
                df.loc[max_index, "strain"],
                df.loc[max_index, "stress_MPa"],
                marker="^",
                s=65,
                label="UTS" if first_uts_label else None,
                zorder=3
            )

            first_uts_label = False

    plt.title(f"Stress-Strain Curves - {material}")
    plt.xlabel("Engineering Strain (mm/mm)")
    plt.ylabel("Engineering Stress (MPa)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save graph
    safe_material = str(material).replace(" ", "_")
    output_file = OUTPUT_DIR / f"stress_strain_{safe_material}.png"

    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Saved: {output_file}")


# --------------------------------------------------
# 2. YIELD STRENGTH BOXPLOT
# --------------------------------------------------

summary["yield_MPa"] = pd.to_numeric(
    summary["yield_MPa"],
    errors="coerce"
)

box_data = []
labels = []

for material in materials:

    values = summary.loc[
        summary["material"] == material,
        "yield_MPa"
    ].dropna()

    if len(values) > 0:
        box_data.append(values)
        labels.append(material)

if box_data:

    plt.figure(figsize=(9, 6))

    plt.boxplot(
        box_data,
        tick_labels=labels,
        showmeans=True
    )

    plt.title("Yield Strength Comparison by Material")
    plt.xlabel("Material")
    plt.ylabel("Yield Strength (MPa)")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    output_file = OUTPUT_DIR / "yield_strength_boxplot.png"

    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Saved: {output_file}")

else:
    print("No valid yield strength data found.")

print("All plots generated successfully!")
