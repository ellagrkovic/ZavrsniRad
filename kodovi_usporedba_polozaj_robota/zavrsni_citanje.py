import json
from ortools.sat.python import cp_model

# Parametri
v = 1
robots = [(5, 10), (15, 10)]
workspaces = [(10, 0), (20, 10)]
num_robots = len(robots)
T_MAX = 50
H = 1000

def run_optimal_cp_sat(items, robots, workspaces, v):
    model = cp_model.CpModel()
    num_items = len(items)

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

    for i in range(num_items):
        model.Add(sum(alpha[k][i] for k in range(num_robots)) == z[i])

    for k in range(num_robots):
        xk, yk = robots[k]
        Wmin, Wmax = workspaces[k]
        for i in range(num_items):
            xi, yi = items[i]
            dy = abs(yk - yi)
            x_pos = model.NewIntVar(-1000, 1000, f'x_pos[{k}][{i}]')
            dx = model.NewIntVar(-1000, 1000, f'dx[{k}][{i}]')
            abs_dx = model.NewIntVar(0, 1000, f'abs_dx[{k}][{i}]')

            model.Add(x_pos == xi - t[i]*v)
            model.Add(dx == xk - x_pos)
            model.AddAbsEquality(abs_dx, dx)
            model.Add(Tk[k][i] == abs_dx + dy)

            tr = max(0, int((xi - Wmin) / v))
            td = max(0, int((xi - Wmax) / v))
            model.Add(t[i] >= tr).OnlyEnforceIf(alpha[k][i])
            model.Add(t[i] <= td).OnlyEnforceIf(alpha[k][i])

    for i in range(num_items):
        for j in range(num_items):
            if i == j:
                continue
            for k in range(num_robots):
                model.Add(t[i] >= t[j] + Tk[k][j] - H * (4 - z[i] - z[j] - alpha[k][i] - alpha[k][j] + beta[i][j]))
                model.Add(t[j] >= t[i] + Tk[k][i] - H * (5 - z[i] - z[j] - alpha[k][i] - alpha[k][j] - beta[i][j]))

    model.Maximize(sum(z))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return int(solver.ObjectiveValue())
    else:
        return 0

# Učitaj testne podatke
with open("kodovi_usporedba_polozaj_robota/testni_podaci_paketa.json", "r") as f:
    test_data = json.load(f)

# Pokreni optimizaciju za sve skupove
summary = []
for category, sets in test_data.items():
    for set_data in sets:
        item_coords = [(item["x"], item["y"]) for item in set_data["items"]]
        result = run_optimal_cp_sat(item_coords, robots, workspaces, v)
        summary.append({
            "set_id": set_data["id"],
            "category": category,
            "num_items": len(item_coords),
            "num_taken": result
        })

# Ispiši rezultate
for r in summary:
    print(f"{r['set_id']}): optimalno preuzeto {r['num_taken']} / {r['num_items']} paketa")
