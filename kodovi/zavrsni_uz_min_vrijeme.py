from ortools.sat.python import cp_model
import random
import matplotlib.pyplot as plt

# Parametri
v = 1
robots = [(5, 10), (15, 10)]  # (x_k, y_k) za k=0,1
workspaces = [(10, 0), (20, 10)]  # (W_{k-1}, W_k) za k=0,1
num_robots = len(robots)

num_items = int(input("Unesi broj paketa: "))

items = []

for i in range(num_items): 
    x = random.randint(20, 50)
    y = random.randint(0, 10)
    items.append((x, y))

# ispis koordinata paketa
for i, item in enumerate(items):
        print(f"Paket{i+1} : ({item[0]}, {item[1]})")

T_MAX = 50
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

# CILJ: Maksimizacija broja uzetih paketa i minimizacija ukupnog trajanja
total_items = sum(z)
total_duration = sum(Tk[k][i] for k in range(num_robots) for i in range(num_items))

# Vaga između ciljeva - eksperimentalno odabran faktor
LAMBDA = 1  # povećaj za jaču penalizaciju vremena

# Kombinirani cilj
model.Maximize(1000 * total_items - LAMBDA * total_duration)


solver = cp_model.CpSolver()
status = solver.Solve(model)

# Ispis
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    num_taken = sum(solver.Value(z[i]) for i in range(num_items))
    print(f'\n[RJEŠENJE] Broj uzetih paketa: {num_taken}\n')
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

