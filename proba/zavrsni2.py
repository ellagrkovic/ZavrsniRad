from ortools.sat.python import cp_model
import math
import random

v = 1.0
items = [(random.randint(20, 50), random.randint(0, 10)) for _ in range(5)]  # Paketi sa slučajnim koordinatama
robots = [(5, 10), (15, 10)]  # Pozicije robota
workspaces = [(0, 10), (10, 20)]  # Pozicije radnih zona

num_items = len(items)
num_robots = len(robots)
H = 1000
T_MAX = 50  

model = cp_model.CpModel()

#tu definiram sve varijable
z = [model.NewBoolVar(f'z[{i}]') for i in range(num_items)]  # Uzima li se predmet sa trake
t = [model.NewIntVar(0, T_MAX, f't[{i}]') for i in range(num_items)]  # Trenutak u kojem se uzima predmet
alpha = [[model.NewBoolVar(f'alpha[{k}][{i}]') for i in range(num_items)] for k in range(num_robots)]  # Dodjela zadatka robotima
beta = [[model.NewBoolVar(f'beta[{i}][{j}]') for j in range(num_items)] for i in range(num_items)]  # Raspored uzimanja paketa

# Lookup tabela za vrijeme potrebno da robot dođe do paketa
Tk_lookup = [[[0 for _ in range(T_MAX + 1)] for i in range(num_items)] for k in range(num_robots)]

for k in range(num_robots):
    xk, yk = robots[k]
    for i in range(num_items):
        xi, yi = items[i]
        #ovdje simulira pomicanje paketa i računanje dohvata za svaki paket
        for ti_val in range(T_MAX + 1):
            x_pos = xi - v * ti_val  
            dist = math.sqrt((xk - x_pos)**2 + (yk - yi)**2)
            Tk_lookup[k][i][ti_val] = int(dist / v + 1) 

# Vrijeme dolaska paketa do radnih zona
trk = [[max(0, int((workspaces[k][0] - items[i][0]) / v)) for i in range(num_items)] for k in range(num_robots)]
tdk = [[max(0, int((workspaces[k][1] - items[i][0]) / v)) for i in range(num_items)] for k in range(num_robots)]


# Dodavanje uvjeta da se predmet mora uzeti
for i in range(num_items):
    model.Add(sum(alpha[k][i] for k in range(num_robots)) == z[i])

# Dodavanje uvjeta za robote i vrijeme uzimanja paketa
for i in range(num_items):
    for k in range(num_robots):
        model.Add(t[i] >= trk[k][i]).OnlyEnforceIf([z[i], alpha[k][i]])  # Paket ne može biti uzet prije nego što stigne u radnu zonu
        model.Add(t[i] <= tdk[k][i]).OnlyEnforceIf([z[i], alpha[k][i]])  # Paket ne može biti uzet nakon što prođe radnu zonu

# Dodavanje uvjeta za redoslijed uzimanja paketa
for i in range(num_items):
    for j in range(num_items):
        if i == j:
            continue
        for k in range(num_robots):
            Tk_i = model.NewIntVar(0, H, f'Tk[{k}][{i}]')
            Tk_j = model.NewIntVar(0, H, f'Tk[{k}][{j}]')
            model.AddElement(t[i], Tk_lookup[k][i], Tk_i)
            model.AddElement(t[j], Tk_lookup[k][j], Tk_j)

            # Dodavanje uvjeta za redoslijed paketa
            model.Add(t[i] >= t[j] + Tk_j - H * (4 - z[i] - z[j] - alpha[k][i] - alpha[k][j] + beta[i][j]))
            model.Add(t[j] >= t[i] + Tk_i - H * (5 - z[i] - z[j] - alpha[k][i] - alpha[k][j] - beta[i][j]))

# Cilj: maksimizirati broj uzetih predmeta
model.Maximize(sum(z))

# Solver
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 50.0
status = solver.Solve(model)

# Ispis rezultata
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(f'\nBroj uzetih predmeta: {int(solver.ObjectiveValue())}\n')

    # Ispis koordinata paketa
    print("Koordinate paketa:")
    for i, item in enumerate(items):
        print(f"paket{i+1}:({item[0]}, {item[1]})")

    # Prvi ispis robota i kada uzimaju pakete
    for i in range(num_items):
        if solver.Value(z[i]):
            print(f'Predmet {i+1} uzet u t = {solver.Value(t[i])}')
            for k in range(num_robots):
                if solver.Value(alpha[k][i]):
                    print(f'  uzima robot {k+1}')
        else:
            print(f'Predmet {i+1} nije uzet')

    # Prikazivanje redoslijeda izvršavanja paketa (beta varijable)
    print("\nRedoslijed izvršavanja (beta):")
    for i in range(num_items):
        for j in range(num_items):
            if i != j and solver.Value(beta[i][j]):
                print(f'  {i+1} prije {j+1}')
else:
    print('Nema rješenja.')
