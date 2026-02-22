import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class Company:
    def __init__(self, name, technologies):
        self.name = name
        self.technologies = technologies

# Offer definition
Company1 = Company("Company 1", [
    {"type": "Oil", "capacity_mw": 100, "bid_price": 200.0, "availability": 1},
    {"type": "Gas", "capacity_mw": 250, "bid_price": 65.5, "availability": 1},
])   

Company2 = Company("Company 2", [
    {"type": "Solar", "capacity_mw": 150, "bid_price": 0.0, "availability": 1},
    {"type": "Coal", "capacity_mw": 200, "bid_price": 45.0, "availability": 0.9}
])

demand_mw = 500.0

# 1. Estrazione, calcolo capacità effettiva e ordinamento
all_bids = [
    {"company": c.name, "effective_capacity": t["capacity_mw"] * t["availability"], **t} 
    for c in [Company1, Company2] for t in c.technologies
]
all_bids.sort(key=lambda x: x["bid_price"])

#PLOT
colors = {"Company 1": "skyblue", "Company 2": "salmon"}
fig, ax = plt.subplots(figsize=(10, 6))

current_x = 0
for bid in all_bids:
    width = bid["effective_capacity"]
    height = bid["bid_price"]
    
    # Crea il blocco proporzionato alla capacità
    ax.bar(current_x, height, width=width, align='edge', 
           color=colors.get(bid["company"], "gray"), edgecolor='black')
    
    # Etichetta della tecnologia sopra il blocco
    ax.text(current_x + width/2, height + 2, bid["type"], ha='center', va='bottom', fontsize=9)
    
    current_x += width

ax.set_xlabel("Capacità Cumulativa (MW)")
ax.set_ylabel("Prezzo (€/MWh)")
ax.set_title("Merit Order Curve")

# Aggiunge la legenda
legend_handles = [mpatches.Patch(color=color, label=company) for company, color in colors.items()]
ax.legend(handles=legend_handles)

plt.savefig("merit_order.png")