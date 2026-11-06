import matplotlib.pyplot as plt
import pandas as pd
import os

os.makedirs('outputs', exist_ok=True)

for i in range(1, 3):
    df = pd.read_csv(f'data/raw/test_{i:02d}.csv')
    # print(df.columns)

    if 'displacement_m' in df.columns:
        displacement_mm = df['displacement_m'] * 1000
    elif 'displacement_mm' in df.columns:
        displacement_mm = df['displacement_mm']
    else:
        print("Displacement column not found")
        continue
    
    force_N = df['force_N']

    plt.plot(displacement_mm, force_N, label='Test 01')

plt.title('Force vs Displacement')
plt.xlabel('Displacement (mm)')
plt.ylabel('Force (N)')
plt.legend()
plt.grid(True)

plt.savefig('outputs/force_vs_displacement.png', dpi=300, bbox_inches='tight')

