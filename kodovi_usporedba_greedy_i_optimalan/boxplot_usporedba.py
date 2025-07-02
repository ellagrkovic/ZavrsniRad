import matplotlib.pyplot as plt

# Podaci
greedy_5 = [5, 4, 4, 5, 5, 5, 3, 4, 3, 5]
optimal_5 = [5] * 10
greedy_10 = [7, 6, 7, 8, 7, 8, 7, 4, 9, 7]
optimal_10 = [10, 10, 10, 10, 9, 9, 8, 8, 10, 9]
greedy_15 = [8, 8, 8, 7, 9, 9, 10, 10, 9, 11]
optimal_15 = [12, 11, 11, 10, 13, 14, 13, 11, 13, 14]

data = [
    greedy_5, optimal_5,
    greedy_10, optimal_10,
    greedy_15, optimal_15
]

labels = [
    "Greedy (5)", "Optimizacijski (5)",
    "Greedy (10)", "Optimizacijski (10)",
    "Greedy (15)", "Optimizacijski (15)"
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
plt.title("Usporedba pohlepnog i optimizacijskog algoritma po broju predmeta", fontsize=14)
plt.ylabel("Broj preuzetih predmeta", fontsize=12)
plt.xticks(rotation=20, fontsize=10)
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle=':', alpha=0.7)

plt.tight_layout()
plt.show()
