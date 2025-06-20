from ortools.sat.python import cp_model
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches

# Parametri
v = 1
robots = [(5, 10), (15, 10)]  # (x_k, y_k) za k=0,1
workspaces = [(10, 0), (20, 10)]  # (W_{k-1}, W_k) za k=0,1
num_robots = len(robots)

num_items = int(input("Unesi broj paketa: "))

items = []

for i in range(num_items): 
    x = random.randint(20, 100)
    y = random.randint(0, 10)
    items.append((x, y))

# ispis koordinata paketa
for i, item in enumerate(items):
        print(f"Paket{i+1} : ({item[0]}, {item[1]})")

T_MAX = 100
H = 1000

model = cp_model.CpModel()

z = []
t = []
alpha = []
beta = []
Tk = []

# z_i - indikator hoće li se paket i uzeti
for i in range(num_items):
    z.append(model.NewBoolVar(f'z[{i}]'))

# t_i - cjelobrojno vrijeme početka dohvaćanja paketa i
for i in range(num_items):
    t.append(model.NewIntVar(0, T_MAX, f't[{i}]'))

# alpha_{k,i} - je li paket i dodijeljen robotu k
for k in range(num_robots):
    row = []
    for i in range(num_items):
        row.append(model.NewBoolVar(f'alpha[{k}][{i}]'))
    alpha.append(row)

# beta_{i,j} - je li i prije j na istom robotu
for i in range(num_items):
    row = []
    for j in range(num_items):
        row.append(model.NewBoolVar(f'beta[{i}][{j}]'))
    beta.append(row)
    
#Tk_{i,k} - vrijeme obrade posla i na stroju k 
for k in range(num_robots):
    row = []
    for i in range(num_items):
        var = model.NewIntVar(0, H, f'Tk[{k}][{i}]')
        row.append(var)
    Tk.append(row)
    
#OGRANIČENJA

# 1) Dodjela: svaki zadatak najviše jednom robotu
for i in range(num_items):
    model.Add(sum(alpha[k][i] for k in range(num_robots)) == z[i]) 

# 2) Trajanje i ograničenja nad vremenima
for k in range(num_robots):
    xk, yk = robots[k]         # pozicija robota k
    Wmin, Wmax = workspaces[k] # radni prostor robota k
    for i in range(num_items):
        xi, yi = items[i]      # početna pozicija paketa i

        # Pozicija paketa u trenutku t_i
        x_pos = model.NewIntVar(-1000, 1000, f'x_pos[{k}][{i}]')  # x_i - v * t_i
        dx = model.NewIntVar(-1000, 1000, f'dx[{k}][{i}]')         # xk - x_pos
        abs_dx = model.NewIntVar(0, 1000, f'abs_dx[{k}][{i}]')     # |dx|
        dy = abs(yk - yi)                                          # |yk - yi| (konstanta)

        model.Add(x_pos == xi - t[i]*v)
        model.Add(dx == xk - x_pos)
        model.AddAbsEquality(abs_dx, dx)
        model.Add(Tk[k][i] == abs_dx + dy)

        # Vrijeme mora biti unutar [release, deadline]
        tr = max(0, int((xi - Wmin) / v))
        td = max(0, int((xi - Wmax) / v))
        model.Add(t[i] >= tr).OnlyEnforceIf(alpha[k][i])
        model.Add(t[i] <= td).OnlyEnforceIf(alpha[k][i])

# 3) Nema preklapanja
for i in range(num_items):
    for j in range(num_items):
        if i == j:
            continue
        for k in range(num_robots):
            model.Add(t[i] >= t[j] + Tk[k][j] - H * (4 - z[i] - z[j] - alpha[k][i] - alpha[k][j] + beta[i][j]))
            model.Add(t[j] >= t[i] + Tk[k][i] - H * (5 - z[i] - z[j] - alpha[k][i] - alpha[k][j] - beta[i][j]))

# Ciljna funkcija: maksimalan broj preuzetih paketa
model.Maximize(sum(z))

# Rješavanje
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Ispis
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(f'\n[RJEŠENJE] Broj uzetih paketa: {int(solver.ObjectiveValue())}\n')
    for i in range(num_items):
        if solver.Value(z[i]):
            print(f'Paket{i+1} uzet u t = {solver.Value(t[i])}')
            for k in range(num_robots):
                if solver.Value(alpha[k][i]):
                    print(f'  uzima robot {k+1}')
                    print(f'  trajanje dohvaćanja: {solver.Value(Tk[k][i])} sekundi\n')
        else:
            print(f'Paket{i+1} nije uzet\n')
else:
    print('Nema rješenja.')
    
# Prikupi informacije za Ganttov dijagram
schedule = []

for i in range(num_items):
    if solver.Value(z[i]):
        t_start = solver.Value(t[i])
        for k in range(num_robots):
            if solver.Value(alpha[k][i]):
                duration = solver.Value(Tk[k][i])
                schedule.append({
                    'robot': k,
                    'item': i,
                    'start': t_start,
                    'duration': duration,
                })

# Iscrtavanje Ganttovog dijagrama
fig, ax = plt.subplots(figsize=(12, 4))
colors = [
    '#4A90E2', 
    '#6A5ACD',  
    '#B19CD9',  
    '#FFB6C1',  
    '#9370DB',  
    '#87CEFA',  
    '#DB7093',  
    '#C71585'   
]

yticks = []
yticklabels = []

for idx, k in enumerate(range(num_robots)):
    yticks.append(idx)
    yticklabels.append(f'Robot {k+1}')
    for task in schedule:
        if task['robot'] == k:
            ax.broken_barh(
                [(task['start'], task['duration'])],
                (idx - 0.4, 0.8),
                facecolors=colors[task['item'] % len(colors)],
                edgecolors='black'
            )
            ax.text(
                task['start'] + task['duration']/2,
                idx,
                f"P{task['item']+1}",
                va='center',
                ha='center',
                color='white',
                fontsize=9,
                fontweight='bold'
            )

ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels)
ax.set_xlabel("Vrijeme (sekunde)")
ax.set_title("Raspored dohvaćanja paketa po robotima")
ax.grid(True)
plt.tight_layout()
plt.show()


# Postavke
max_time = 100  # maksimalno vrijeme simulacije u sekundama
frame_interval = 100  # ms između frameova
item_speed = 1 * (frame_interval / 1000)  # 1 jedinica po sekundi
num_frames = int(max_time * 1000 / frame_interval)  # broj frameova

# Kopija početnih pozicija paketa za simulaciju
item_positions = [list(pos) for pos in items]  # mutable pozicije
active_items = [True] * len(items)  # status svakog paketa

# Povežimo paket s planom dohvaćanja iz rasporeda
pickup_schedule = {}
for task in schedule:
    pickup_time = task['start']  # Paket nestaje na POČETKU dohvaćanja
    pickup_schedule[f"P{task['item']+1}"] = {
        'robot': task['robot'],
        'time': pickup_time
    }

fig, ax = plt.subplots(figsize=(12, 6))

# Iscrtaj radne prostore
for idx, (x1, x2) in enumerate(workspaces):
    ax.add_patch(
        mpatches.Rectangle((x1, 0), x2 - x1, 10,
                           facecolor='gray', alpha=0.2,
                           label=f'Workspace {idx+1}' if idx == 0 else None)
    )

# Iscrtaj robote
for idx, (x, y) in enumerate(robots):
    ax.plot(x, y, 'o', color='black')
    ax.text(x, y + 0.5, f'Robot {idx+1}', ha='center', fontsize=9)

# Inicijalno crtanje paketa
item_squares = []
item_labels = []
for idx, (x, y) in enumerate(item_positions):
    paket_id = f"P{idx+1}"
    square, = ax.plot([x], [y], 's', color='red', label='Paketi' if idx == 0 else None)
    label = ax.text(x, y + 0.3, paket_id, fontsize=8, ha='center')
    item_squares.append(square)
    item_labels.append(label)

# Dodaj prikaz vremena
time_text = ax.text(0.95, 0.95, '', transform=ax.transAxes,
                    ha='right', va='top', fontsize=10, bbox=dict(facecolor='white', alpha=0.7))

ax.set_xlim(0, max(x for x, _ in items) + 5)
ax.set_ylim(-1, 12)
ax.set_title("Animacija kretanja i preuzimanja paketa")
ax.legend()
ax.grid(True)

# Animacijska funkcija
def update(frame):
    current_time = frame * frame_interval / 1000  # pretvori frame u vrijeme u sekundama

    for i, (x, y) in enumerate(item_positions):
        paket_id = f"P{i+1}"
        if not active_items[i]:
            item_squares[i].set_data([], [])
            item_labels[i].set_position((-100, -100))  # pomakni izvan prikaza
            continue

        # Pomak ulijevo
        x -= item_speed
        item_positions[i][0] = x

        # Provjeri je li vrijeme za preuzimanje
        if paket_id in pickup_schedule and current_time >= pickup_schedule[paket_id]['time']:
            active_items[i] = False
            item_squares[i].set_data([], [])
            item_labels[i].set_position((-100, -100))
        else:
            item_squares[i].set_data([x], [y])
            item_labels[i].set_position((x, y + 0.3))

    time_text.set_text(f'Time: {current_time:.1f}s')
    return item_squares + item_labels + [time_text]

ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=frame_interval, blit=True)
plt.tight_layout()
plt.show()
#ani.save("kodovi/kretanje.gif", writer='pillow', fps=10)
