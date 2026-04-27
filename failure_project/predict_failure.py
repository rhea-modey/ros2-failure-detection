import csv
import glob
import math

def analyze(filename):
    rows = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "time": float(r["time"]),
                "x": float(r["x"]),
                "y": float(r["y"]),
                "linear": float(r["linear"]),
                "angular": float(r["angular"]),
            })

    if len(rows) < 2:
        return None

    start = rows[0]
    end = rows[-1]

    displacement = math.sqrt((end["x"] - start["x"])**2 + (end["y"] - start["y"])**2)

    moving_rows = sum(1 for r in rows if abs(r["linear"]) > 0.01)
    rotating_rows = sum(1 for r in rows if abs(r["angular"]) > 0.1)

    # Heuristic from your data:
    # aborted runs had tiny displacement + no forward movement + lots of rotation
    failure = displacement < 0.15 and moving_rows < 3 and rotating_rows > 5

    return displacement, moving_rows, rotating_rows, failure

for file in sorted(glob.glob("run_*.csv")):
    result = analyze(file)
    if result is None:
        continue

    displacement, moving_rows, rotating_rows, failure = result
    prediction = "FAILURE" if failure else "OK / SUCCESS-LIKE"

    print(f"\n{file}")
    print(f"  displacement: {displacement:.3f}")
    print(f"  moving_rows: {moving_rows}")
    print(f"  rotating_rows: {rotating_rows}")
    print(f"  prediction: {prediction}")