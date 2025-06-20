import matplotlib.pyplot as plt

# Podaci
optimal_reverse_robots_5 = [5] * 10
optimal_5 = [5] * 10
optimal_reverse_robots_10 = [10] * 10
optimal_10 = [10, 10, 10, 10, 9, 9, 8, 8, 10, 9]
optimal_reverse_robots_15 = [15, 14, 14, 14, 14, 15, 13, 14, 15, 15]
optimal_15 = [12, 11, 11, 10, 13, 14, 13, 11, 13, 14]

data = [
    optimal_reverse_robots_5, optimal_5,
    optimal_reverse_robots_10, optimal_10,
    optimal_reverse_robots_15, optimal_15
]

labels = [
    "Optimalni - obrnuti roboti (5)", "Optimalni (5)",
    "Optimalni - obrnuti roboti (10)", "Optimalni (10)",
    "Optimalni - obrnuti roboti (15)", "Optimalni (15)"
]

colors = ["#FF9999", "#99CCFF", "#FF9999", "#99CCFF", "#FF9999", "#99CCFF"]

# Crtanje poboljšanog boxplota
plt.figure(figsize=(12, 6))
box = plt.boxplot(data, patch_artist=True, labels=labels)

# Boje kutija
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_edgecolor("black")
    patch.set_linewidth(1.2)

# Poboljšani stilovi
for whisker in box['whiskers']:
    whisker.set(color='black', linewidth=1.2, linestyle="--")

for cap in box['caps']:
    cap.set(color='black', linewidth=1.2)

for median in box['medians']:
    median.set(color='black', linewidth=2)

# Naslovi i osi
plt.title("Usporedba Optimalnih algoritama u ovisnosti o položaju robota", fontsize=14)
plt.ylabel("Broj preuzetih paketa", fontsize=12)
plt.xticks(rotation=20, fontsize=10)
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle=':', alpha=0.7)

plt.tight_layout()
plt.show()
