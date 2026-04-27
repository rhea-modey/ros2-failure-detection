import csv
import math
import glob

def analyze_file(filename):
    rows = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "time": float(row["time"]),
                "x": float(row["x"]),
                "y": float(row["y"]),
                "linear": float(row["linear"]),
                "angular": float(row["angular"]),
            })

    if len(rows) < 2:
        return None

    start = rows[0]
    end = rows[-1]

    total_dist = 0.0
    moving_rows = 0
    rotating_rows = 0

    for i in range(1, len(rows)):
        dx = rows[i]["x"] - rows[i-1]["x"]
        dy = rows[i]["y"] - rows[i-1]["y"]
        total_dist += math.sqrt(dx*dx + dy*dy)

        if abs(rows[i]["linear"]) > 0.01:
            moving_rows += 1
        if abs(rows[i]["angular"]) > 0.1:
            rotating_rows += 1

    duration = end["time"] - start["time"]
    displacement = math.sqrt((end["x"] - start["x"])**2 + (end["y"] - start["y"])**2)

    return {
        "file": filename,
        "duration": duration,
        "start_x": start["x"],
        "start_y": start["y"],
        "end_x": end["x"],
        "end_y": end["y"],
        "displacement": displacement,
        "total_distance": total_dist,
        "moving_rows": moving_rows,
        "rotating_rows": rotating_rows,
        "label": "aborted" if "aborted" in filename else "success" if "success" in filename else "unknown",
    }

for filename in sorted(glob.glob("run_*.csv")):
    result = analyze_file(filename)
    if result is None:
        continue

    print("\n" + result["file"])
    print(f"  label: {result['label']}")
    print(f"  duration: {result['duration']:.2f} sec")
    print(f"  start: ({result['start_x']:.2f}, {result['start_y']:.2f})")
    print(f"  end:   ({result['end_x']:.2f}, {result['end_y']:.2f})")
    print(f"  displacement: {result['displacement']:.3f}")
    print(f"  total_distance: {result['total_distance']:.3f}")
    print(f"  moving_rows: {result['moving_rows']}")
    print(f"  rotating_rows: {result['rotating_rows']}")