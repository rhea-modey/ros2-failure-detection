import glob
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Load CSV files
# ---------------------------
files = sorted(glob.glob("run_*.csv"))
runs = {file: pd.read_csv(file) for file in files}

# ---------------------------
# Global figure style
# ---------------------------
plt.rcParams.update({
    "figure.figsize": (9, 6),
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 15,
    "legend.fontsize": 11,
    "xtick.labelsize": 11,
    "ytick.labelsize": 12,
    "lines.linewidth": 2.5,
})


def compute_metrics(df):
    start = df.iloc[0]
    end = df.iloc[-1]

    displacement = math.sqrt((end["x"] - start["x"]) ** 2 + (end["y"] - start["y"]) ** 2)

    total_distance = 0.0
    for i in range(1, len(df)):
        dx = df.iloc[i]["x"] - df.iloc[i - 1]["x"]
        dy = df.iloc[i]["y"] - df.iloc[i - 1]["y"]
        total_distance += math.sqrt(dx ** 2 + dy ** 2)

    moving_rows = (df["linear"].abs() > 0.01).sum()
    rotating_rows = (df["angular"].abs() > 0.1).sum()
    duration = df["time"].iloc[-1] - df["time"].iloc[0]

    return displacement, total_distance, moving_rows, rotating_rows, duration


# ---------------------------
# 1. Trajectory Plot
# ---------------------------
plt.figure(figsize=(8, 8))

for file, df in runs.items():
    if "success" in file:
        plt.plot(df["x"], df["y"], label=file.replace(".csv", ""), linewidth=3)
    else:
        plt.plot(df["x"], df["y"], linestyle="--", label=file.replace(".csv", ""), linewidth=3)

plt.title("Robot Trajectories: Successful vs. Aborted Runs")
plt.xlabel("X Position (m)")
plt.ylabel("Y Position (m)")
plt.grid(True, alpha=0.3)
plt.axis("equal")
plt.legend(loc="best")
plt.tight_layout()
plt.savefig("figure_1_trajectory_plot.png", dpi=300)
plt.show()


# ---------------------------
# 2. Average Displacement with Error Bars
# ---------------------------
success_disp = []
failure_disp = []

for file, df in runs.items():
    disp, _, _, _, _ = compute_metrics(df)
    if "success" in file:
        success_disp.append(disp)
    else:
        failure_disp.append(disp)

success_mean = np.mean(success_disp)
failure_mean = np.mean(failure_disp)

success_std = np.std(success_disp)
failure_std = np.std(failure_disp)

plt.figure(figsize=(7, 6))
plt.bar(
    ["Successful Runs", "Aborted Runs"],
    [success_mean, failure_mean],
    yerr=[success_std, failure_std],
    capsize=8
)

plt.title("Average Displacement by Run Outcome")
plt.ylabel("Displacement (m)")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("figure_2_average_displacement.png", dpi=300)
plt.show()


# ---------------------------
# 3. Movement vs Rotation
# ---------------------------
names = []
moving = []
rotating = []

for file, df in runs.items():
    _, _, move, rot, _ = compute_metrics(df)
    names.append(file.replace(".csv", ""))
    moving.append(move)
    rotating.append(rot)

x = range(len(names))
width = 0.38

plt.figure(figsize=(11, 6))
plt.bar([i - width / 2 for i in x], moving, width=width, label="Forward Movement")
plt.bar([i + width / 2 for i in x], rotating, width=width, label="Rotation")

plt.title("Movement vs Rotation Across Runs")
plt.ylabel("Count")
plt.xticks(list(x), names, rotation=30, ha="right")
plt.grid(axis="y", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("figure_3_movement_vs_rotation.png", dpi=300)
plt.show()


# ---------------------------
# 4. Velocity Time Series
# ---------------------------
success_file = next((f for f in files if "success" in f), None)
failure_file = next((f for f in files if "aborted" in f or "failure" in f), None)

for file in [success_file, failure_file]:
    if file is None:
        continue

    df = runs[file].copy()
    df["time_relative"] = df["time"] - df["time"].iloc[0]

    plt.figure(figsize=(10, 6))
    plt.plot(df["time_relative"], df["linear"], label="Linear Velocity")
    plt.plot(df["time_relative"], df["angular"], label="Angular Velocity")

    plt.title(f"Velocity Profile: {file.replace('.csv', '')}")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"figure_4_velocity_{file.replace('.csv', '')}.png", dpi=300)
    plt.show()


# ---------------------------
# 5. Print Summary
# ---------------------------
print("\n=== Run Metrics ===")

for file, df in runs.items():
    disp, dist, move, rot, dur = compute_metrics(df)
    label = "success" if "success" in file else "failure"

    print(f"\n{file}")
    print(f"  Label: {label}")
    print(f"  Duration: {dur:.2f} sec")
    print(f"  Displacement: {disp:.3f} m")
    print(f"  Total Distance: {dist:.3f} m")
    print(f"  Movement Steps: {move}")
    print(f"  Rotation Steps: {rot}")