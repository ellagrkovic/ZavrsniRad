import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random

# Parametri
v = 1
robots = [(5, 10), (15, 10)]
workspaces = [(10, 0), (20, 10)]
num_robots = len(robots)

# Generiraj pakete
num_items = int(input("Unesi broj predmeta: "))
# items = [(44, 6), (38, 2), (27, 9), (35, 1), (30, 4), (25, 8)]

items = []

for i in range(num_items): 
    x = random.randint(20, 50)
    y = random.randint(0, 10)
    items.append((x, y))

# Prikaži koordinate
for i, (x, y) in enumerate(items):
    print(f'Predmet{i+1} : ({x}, {y})')

# Greedy dodjela
robot_timeline = []
for robot_id in range(num_robots):
    robot_timeline.append([])

results = []

for i, (xi, yi) in enumerate(items):
    best_assignment = None
    for k in range(num_robots):
        xk, yk = robots[k]
        Wmin, Wmax = workspaces[k]
        tr = max(0, int((xi - Wmin) / v))
        td = max(0, int((xi - Wmax) / v))
        dy = abs(yk - yi)

        for t_candidate in range(tr, td + 1):
            x_current = xi - v * t_candidate
            dist_x = abs(xk - x_current)
            Tk_val = dist_x + dy

            # Provjera preklapanja
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

# --- Ispis rezultata greedy algoritma ---
print(f'\n[RJEŠENJE - GREEDY] Broj uzetih predmeta: {sum(1 for r in results if r["robot"] is not None)}\n')

for task in results:
    i = task['item']
    if task['robot'] is not None:
        print(f'Predmet{i+1} uzet u t = {task["start"]}')
        print(f'  uzima robot {task["robot"]+1}')
        print(f'  trajanje dohvaćanja: {task["duration"]} sekundi\n')
    else:
        print(f'Paket{i+1} nije uzet\n')


# --- Ganttov dijagram ---
fig, ax = plt.subplots(figsize=(12, 4))
colors = ['#4A90E2', '#6A5ACD', '#B19CD9', '#FFB6C1', '#9370DB', '#87CEFA']

for k in range(num_robots):
    for task in results:
        if task['robot'] == k:
            ax.broken_barh(
                [(task['start'], task['duration'])],
                (k - 0.4, 0.8),
                facecolors=colors[task['item'] % len(colors)],
                edgecolors='black'
            )
            ax.text(
                task['start'] + task['duration'] / 2,
                k,
                f"P{task['item']+1}",
                va='center',
                ha='center',
                color='white',
                fontsize=8,
                fontweight='bold'
            )

ax.set_xlabel("Vrijeme")
ax.set_yticks(range(num_robots))
ax.set_yticklabels([f'Robot {k+1}' for k in range(num_robots)])
ax.set_title("Greedy Gantt raspored")
ax.grid(True)
plt.tight_layout()
plt.show()



