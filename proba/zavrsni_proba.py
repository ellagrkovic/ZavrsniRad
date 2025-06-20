import random
import math
import matplotlib.pyplot as plt
import time


def generate_input(num_packages, v_paket = 1):
    roboti = {
        'robot_0': {"position": (5, 10), "w_k-1": 0, "w_k": 10},
        'robot_1': {"position": (15, 10), "w_k-1": 10, "w_k": 20}
    }

    paketi = {} 
    vremena = {}

    for i in range(num_packages):
        paket_id = f'paket_{i}'
        xi0 = random.randint(20, 50)
        yi0 = random.randint(0, 10)
        paketi[paket_id] = (xi0, yi0)  #paketi = { 'paket_0': (35, 4), 'paket_1': (47, 2),..}
        vremena[paket_id] = {"init": (xi0, yi0), "vrijeme": {}}

        for robot_id, robot_data in roboti.items():
            Wk = robot_data["w_k"]
            Wk_1 = robot_data["w_k-1"]

            tr_ik = (xi0 - Wk) / v_paket  
            td_ik = (xi0 - Wk_1) / v_paket

            vremena[paket_id]["vrijeme"][robot_id] = {"tr_ik": tr_ik, "td_ik": td_ik}
            
    #vremena = {
        #'paket_0': {
            # 'init': (35, 4), 
            # 'vrijeme': {
                    #'robot_0': {
                        # 'tr_ik': 25,
                        # 'td_ik': 35
                    # },
                    #'robot_1': {
                        # 'tr_ik': 15
                        # 'td_ik': 25
                    # }
               # }
        # },
    # ...
    #}

    return roboti, paketi, vremena


def plot_state(roboti, paketi, t):
    plt.figure(figsize=(10, 5))
    
    for robot_id, robot_data in roboti.items():
        w_k1, w_k = robot_data["w_k-1"], robot_data["w_k"]
        plt.axvline(w_k1, color='black', linestyle='--')
        plt.axvline(w_k, color='black', linestyle='--')
    
    plt.axhline(0, color='black', linestyle='-')
    plt.axhline(10, color='black', linestyle='-')

    for robot_id, robot_data in roboti.items():
        x, y = robot_data["position"]
        plt.scatter(x, y, label=f"{robot_id}", s=200, marker='s', edgecolor='black')

    for paket_id, (x, y) in paketi.items():
        plt.scatter(x, y, color='red', s=100)
        plt.text(x, y, paket_id, fontsize=9, color='darkred')

    plt.xlim(0, 55)
    plt.ylim(-5, 15)
    plt.xlabel("X (Pokretna traka)")
    plt.ylabel("Y (Visina)")
    plt.title(f"Stanje u sekundi: {t}")
    plt.legend()
    plt.grid()
    plt.show()


def update_packages(paketi, v_paket=1): #simulacija pomaka
    updated = {}
    for paket_id, (x, y) in paketi.items():
        new_x = x - v_paket 
        updated[paket_id] = (new_x, y)
    return updated


def izracunaj_vremena_i_Tk(roboti, paketi, vremena, t, v_paket=1):
    for paket_id, (xi, yi) in paketi.items():
        xi0, yi0 = vremena[paket_id]["init"]
        print(f"\n{paket_id} pozicija u t={t}: ({xi}, {yi})")
        for robot_id, robot_data in roboti.items():
            xk, yk = robot_data["position"] 
            Wk_minus_1 = robot_data["w_k-1"]
            Wk = robot_data["w_k"]

            tr_ik = vremena[paket_id]["vrijeme"][robot_id]["tr_ik"]
            td_ik = vremena[paket_id]["vrijeme"][robot_id]["td_ik"]

            x_t = xi  # trenutna pozicija (već ažurirana u paketi)

            if x_t < Wk_minus_1 or x_t > Wk:
                Tk_i = "izvan dosega"
            else:
                try:
                    Tk_i = math.sqrt((xk - x_t) ** 2 + (yk - yi) ** 2) / v_paket
                    Tk_i = round(Tk_i, 2)
                except:
                    Tk_i = "nedefinirano"

            print(f"  {robot_id}: tr_ik = {tr_ik:.2f}, td_ik = {td_ik:.2f}, f(t={t}) = {Tk_i}")


def run_simulation(steps, num_packages=5, v_paket=1):
    roboti, paketi, vremena = generate_input(num_packages)

    for t in range(steps):
        print(f"\nDetaljni prikaz za t = {t}:")
        print(f"\nPaketi: {paketi}")
        izracunaj_vremena_i_Tk(roboti, paketi, vremena, t, v_paket)
        plot_state(roboti, paketi, t)
        paketi = update_packages(paketi, v_paket)


run_simulation(steps=15, num_packages=5)
