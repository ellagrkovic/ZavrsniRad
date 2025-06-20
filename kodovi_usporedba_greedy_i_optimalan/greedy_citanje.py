import json

# Parametri
v = 1
robots = [(5, 10), (15, 10)]
workspaces = [(10, 0), (20, 10)]
num_robots = len(robots)

# Funkcija za pokretanje greedy algoritma
def run_greedy(items, robots, workspaces, v):
    robot_timeline = [[] for _ in range(len(robots))]
    results = []

    for i, (xi, yi) in enumerate(items):
        best_assignment = None
        for k in range(len(robots)):
            xk, yk = robots[k]
            Wmin, Wmax = workspaces[k]
            tr = max(0, int((xi - Wmin) / v))
            td = max(0, int((xi - Wmax) / v))
            dy = abs(yk - yi)

            for t_candidate in range(tr, td + 1):
                x_current = xi - v * t_candidate
                dist_x = abs(xk - x_current)
                Tk_val = dist_x + dy

                conflict = False
                for (start, dur) in robot_timeline[k]:
                    if not (t_candidate + Tk_val <= start or t_candidate >= start + dur):
                        conflict = True
                        break

                if not conflict:
                    best_assignment = (k, t_candidate, Tk_val)
                    break
            if best_assignment:
                break

        if best_assignment:
            k, t_start, duration = best_assignment
            robot_timeline[k].append((t_start, duration))
            results.append({'item': i, 'robot': k, 'start': t_start, 'duration': duration})
        else:
            results.append({'item': i, 'robot': None})

    return results

# Učitavanje testnih skupova
with open("kodovi_usporedba_greedy_i_optimalan/testni_podaci_paketa.json", "r") as f:
    test_data = json.load(f)

# Pokretanje greedy algoritma nad svim skupovima
greedy_results_summary = []

for category, sets in test_data.items():
    for set_data in sets:
        item_coords = [(item["x"], item["y"]) for item in set_data["items"]]
        result = run_greedy(item_coords, robots, workspaces, v)
        count_taken = sum(1 for r in result if r["robot"] is not None)
        greedy_results_summary.append({
            "set_id": set_data["id"],
            "category": category,
            "num_items": len(item_coords),
            "num_taken": count_taken
        })

# Ispis rezultata
for r in greedy_results_summary:
    print(f"{r['set_id']}: preuzeto {r['num_taken']} / {r['num_items']} paketa")
