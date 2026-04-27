import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# SELECT YOUR RUNS HERE
# ---------------------------
success_file = "run_3_success.csv"   # choose your clean success
failure_file = "run_2_aborted.csv"  # choose your clear failure

# ---------------------------
# LOAD DATA
# ---------------------------
success = pd.read_csv(success_file)
failure = pd.read_csv(failure_file)

# ---------------------------
# PLOT
# ---------------------------
plt.figure(figsize=(7, 7))

# Success trajectory
plt.plot(
    success["x"],
    success["y"],
    color="green",
    linewidth=3,
    label="Successful Run"
)

# Failure trajectory
plt.plot(
    failure["x"],
    failure["y"],
    color="red",
    linestyle="--",
    linewidth=3,
    label="Aborted Run"
)

# Mark start points
plt.scatter(success["x"].iloc[0], success["y"].iloc[0], color="black", s=60, label="Start")
plt.scatter(failure["x"].iloc[0], failure["y"].iloc[0], color="black", s=60)

# Mark end points
plt.scatter(success["x"].iloc[-1], success["y"].iloc[-1], color="green", s=80, marker="X", label="Success End")
plt.scatter(failure["x"].iloc[-1], failure["y"].iloc[-1], color="red", s=80, marker="X", label="Failure End")

# Labels and styling
plt.title("Robot Trajectory: Successful vs. Failed Navigation")
plt.xlabel("X Position (m)")
plt.ylabel("Y Position (m)")
plt.grid(True, alpha=0.3)
plt.axis("equal")
plt.legend()

plt.tight_layout()
plt.savefig("figure_clean_trajectory.png", dpi=300)
plt.show()