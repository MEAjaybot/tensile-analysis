# Python-Based Tensile Test Data Analysis and Material Property Evaluation

**Project:** Tensile Test Data Analysis  
**Tools and Libraries:** Python, Pandas, NumPy, Matplotlib  
**Dataset:** 30 tensile test CSV files with specimen metadata  
**Materials:** Steel, Aluminium and Copper  
**Output:** Processed stress-strain data, material properties, summary statistics and plots

# Motivation for the Work

The main motivation of this project is to automate the analysis of tensile test data and extract important mechanical properties of engineering materials using Python.

Tensile testing generates experimental data containing force and displacement measurements. Manually processing multiple test files can be time-consuming and may introduce calculation errors.

This project aims to develop a reusable Python-based workflow that processes multiple tensile test datasets, calculates mechanical properties and compares the performance of different materials.

# The Problem and Limitation Identification

1. Tensile testing produces large amounts of raw force and displacement data that require processing before mechanical properties can be determined.
2. Raw CSV files may have inconsistent column names or measurement units.
3. Calculating stress and strain manually for multiple specimens is repetitive and time-consuming.
4. Determining Young's modulus requires identifying the elastic region of the stress-strain curve.
5. Yield strength determination using the 0.2% offset method requires additional calculations and interpolation.
6. Identifying specimen fracture from experimental force data can be difficult because the force response may not show a clear drop.
7. Comparing the mechanical properties of different materials requires organizing the results into a consistent format.

# What Does the Previous Manual Approach Lack?

Traditional manual analysis requires processing each tensile test individually. This makes it difficult to maintain consistency when dealing with a large number of specimens.

Manual calculations and spreadsheet-based workflows can also introduce errors in unit conversion, stress calculation and strain calculation.

Furthermore, extracting Young's modulus and 0.2% offset yield strength requires selecting the appropriate region of the stress-strain curve.

An automated Python workflow helps address these problems by applying consistent calculations to multiple test files and generating a combined summary.

# Key Contributions

1. Developed a Python-based workflow to process multiple tensile test datasets.
2. Implemented stress and strain calculations using specimen dimensions and experimental force-displacement data.
3. Implemented Young's modulus calculation using linear regression over a selected elastic strain range.
4. Implemented the 0.2% offset method to estimate yield strength.
5. Developed a fracture-detection method based on the reduction in force after maximum load.
6. Implemented a campaign-based structure to manage multiple tensile tests and collect their results.
7. Generated a summary CSV file and material-wise average mechanical properties.

# Related Methods Used in Tensile Test Analysis

1. **Stress Calculation:** Engineering stress is calculated by dividing the applied force by the original cross-sectional area of the specimen.
2. **Strain Calculation:** Engineering strain is calculated by dividing the displacement by the original gauge length.
3. **Young's Modulus:** The elastic modulus is estimated from the slope of the stress-strain curve within the selected elastic region.
4. **0.2% Offset Yield Strength:** A line parallel to the elastic-region slope is shifted by 0.002 strain. Its intersection with the stress-strain curve is used to estimate yield strength.
5. **Ultimate Tensile Strength (UTS):** UTS is the maximum engineering stress recorded during the tensile test. In this project, it is reported only when fracture is detected.
6. **Fracture Strain:** The strain value at the detected fracture point is used to estimate elongation at fracture.

# Methods

## 1. Dataset and Input Data

The project uses 30 tensile test CSV files representing three materials:

- Steel
- Aluminium
- Copper

A separate metadata file, `specimens.csv`, stores specimen information.

The metadata includes:

- Test ID
- Material
- Cross-sectional area (mm²)
- Gauge length (mm)

The raw experimental data contains force and displacement measurements.

## 2. Data Processing

The raw experimental data is processed before mechanical properties are calculated.

1. Read the experimental CSV files.
2. Identify the force and displacement columns.
3. Convert displacement measurements into millimetres where necessary.
4. Load specimen dimensions from the metadata file.
5. Calculate engineering stress and strain.
6. Store the processed stress-strain data for each specimen.

The equations used are:

Engineering stress:

\[
\sigma = \frac{F}{A_0}
\]

Engineering strain:

\[
\varepsilon = \frac{\Delta L}{L_0}
\]

Where:

- \(F\) = Applied force (N)
- \(A_0\) = Original cross-sectional area (mm²)
- \(\Delta L\) = Displacement (mm)
- \(L_0\) = Original gauge length (mm)

Since force is measured in Newtons and area in mm², stress is obtained in MPa.

## 3. Young's Modulus Calculation

Young's modulus represents the stiffness of a material.

It is calculated from the slope of the stress-strain curve in the elastic region.

\[
E = \frac{\Delta \sigma}{\Delta \varepsilon}
\]

The project uses linear regression with NumPy's `polyfit()` function.

The selected strain range is:

\[
0.0005 \leq \varepsilon \leq 0.002
\]

The slope is divided by 1000 to convert the result from MPa to GPa.

## 4. Yield Strength Calculation

The project uses the 0.2% offset method to estimate yield strength.

1. Fit a straight line to the selected elastic region.
2. Calculate the elastic slope.
3. Shift the fitted line by 0.002 strain.
4. Compare the offset line with the experimental stress-strain curve.
5. Find the intersection using adjacent-point sign changes.
6. Use linear interpolation to estimate the corresponding yield stress.

This method provides an estimate of yield strength when a clear yield point is not present.

## 5. Fracture Detection

The project uses a force-drop-based method to identify fracture.

1. Extract the force measurements.
2. Find the maximum force during the test.
3. Consider the force measurements after the maximum force.
4. Check whether any subsequent force value drops to 50% or less of the maximum force.
5. If the condition is satisfied, classify the test as complete.

The detection condition is:

\[
F_{\text{after peak}} \leq 0.5F_{\text{max}}
\]

If fracture is detected, the test is marked `True`; otherwise, it is marked `False`.

This is a heuristic fracture-detection method and does not independently confirm physical specimen fracture.

## 6. Software Architecture

The project is divided into three main Python files.

**specimen.py**

- Defines the `Specimen` dataclass.
- Defines the `TensileTest` class.
- Calculates stress and strain.
- Calculates Young's modulus.
- Calculates 0.2% offset yield strength.
- Detects fracture and estimates fracture strain.

**campaign.py**

- Defines the `TestCampaign` class.
- Stores multiple tensile test objects.
- Collects the calculated properties from each test.
- Generates a combined Pandas DataFrame.
- Saves the final summary CSV.

**main.py**

- Reads specimen metadata.
- Iterates through the test records.
- Creates specimen and tensile test objects.
- Processes each test.
- Handles invalid files using exception handling.
- Adds valid tests to the campaign.
- Calculates average mechanical properties by material using `groupby()`.

# How Is the Data Processed?

The overall workflow is:

1. Read specimen metadata.
2. Load individual processed tensile test files.
3. Create a specimen object.
4. Create a tensile test object.
5. Calculate stress and strain.
6. Calculate Young's modulus and yield strength.
7. Detect fracture and calculate UTS and fracture strain where applicable.
8. Add the test to the campaign.
9. Collect all test results into a summary DataFrame.
10. Group the results by material and calculate average properties.
11. Save the final results in `outputs/summary.csv`.

# Experiments and Results

## 1. Evaluation Parameters

The project evaluates the following mechanical properties:

- Young's modulus (GPa)
- Yield strength (MPa)
- Ultimate tensile strength (MPa)
- Fracture strain
- Test completion status

## 2. Young's Modulus Results

Based on the generated summary, the approximate average Young's modulus values are:

| Material | Average Young's Modulus |
|---|---:|
| Steel | 197.9 GPa |
| Aluminium | 69.8 GPa |
| Copper | 93.5 GPa |

Steel has the highest average Young's modulus, indicating that it is the stiffest material among the three materials in this dataset.

## 3. Yield Strength Results

The approximate average yield strength values are:

| Material | Average Yield Strength |
|---|---:|
| Steel | 355 MPa |
| Aluminium | 244 MPa |
| Copper | 152 MPa |

Steel has the highest average yield strength, followed by aluminium and copper.

## 4. Ultimate Tensile Strength and Fracture Detection

The current summary identifies only one complete test out of 30 specimens.

- `test_05` was detected as complete.
- `test_01` to `test_04` and `test_06` to `test_30` were flagged as incomplete.
- UTS and fracture strain are therefore unavailable for the other 29 tests.
- A reliable comparison of average UTS across all three materials cannot yet be made.

## 5. Material Comparison

Based on the available Young's modulus and yield strength results:

- Steel is the stiffest material.
- Steel has the highest average yield strength.
- Aluminium has a lower average modulus and yield strength than steel.
- Copper has a lower average yield strength than both steel and aluminium.

These comparisons are based on the current generated dataset and analysis results.

# Limitations of the Project

- The fracture-detection method relies on a fixed 50% force-drop threshold.
- A force drop does not always confirm physical specimen fracture.
- Only one out of 30 tests was detected as complete in the current results.
- UTS comparison across materials is limited by the incomplete fracture detections.
- Young's modulus depends on the selected strain interval.
- The 0.2% offset method depends on the quality of the elastic-region fit and the available experimental data.
- Experimental noise and measurement errors can affect the calculated properties.
- The current analysis uses engineering stress and strain rather than true stress and strain.
- The project does not currently use machine learning to predict material properties or classify fracture behaviour.

# Conclusion

This project demonstrates how Python can automate the processing and analysis of tensile test data for multiple engineering materials. The developed workflow calculates important mechanical properties, organizes test results and compares materials using Pandas. Based on the current results, steel shows the highest stiffness and yield strength. However, the fracture-detection method needs further validation because only one test was classified as complete. Improving fracture detection and validating the calculations against experimental observations would make the analysis more reliable.