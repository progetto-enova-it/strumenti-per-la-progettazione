import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

class Company:
    registry = []

    def __init__(self, name, technologies):
        self.name = name
        self.technologies = technologies
        Company.registry.append(self)

# 1. Definizione Offerte di Produzione (Supply)
Company("Company 1", [
    {"type": "Oil", "capacity_mw": 100, "bid_price": 200.0, "availability": 1},
    {"type": "Gas", "capacity_mw": 250, "bid_price": 60, "availability": 1},
])   

Company("Company 2", [
    {"type": "Solar", "capacity_mw": 150, "bid_price": 0.0, "availability": 1},
    {"type": "Coal", "capacity_mw": 200, "bid_price": 45.0, "availability": 0.9}
])

# 2. Definizione Offerte di Acquisto (Domanda elastica)
demand_bids = [
    {"quantity": 200, "price": 200.0},
    {"quantity": 100, "price": 100.0},
    {"quantity": 100, "price": 50.0},
    {"quantity": 40, "price": 20.0}
]

# 3. Estrazione e Ordinamento Curve
supply_bids = sorted([
    {"company": c.name, "effective_capacity": t["capacity_mw"] * t["availability"], **t} 
    for c in Company.registry for t in c.technologies
], key=lambda x: x["bid_price"])

demand_bids = sorted(demand_bids, key=lambda x: x["price"], reverse=True)

# 4. Calcolo Market Clearing Point (Intersezione)
market_price = 0.0
market_quantity = 0.0

s_idx, d_idx = 0, 0
s_used, d_used = 0, 0

while s_idx < len(supply_bids) and d_idx < len(demand_bids):
    s = supply_bids[s_idx]
    d = demand_bids[d_idx]
    
    s_avail = s["effective_capacity"] - s_used
    d_avail = d["quantity"] - d_used
    
    if d["price"] >= s["bid_price"]:
        cleared = min(s_avail, d_avail)
        market_quantity += cleared
        market_price = s["bid_price"] # Il prezzo è fissato dall'ultimo blocco di offerta accettato
        
        s_used += cleared
        d_used += cleared
        
        if s_used >= s["effective_capacity"]:
            s_idx += 1
            s_used = 0
        if d_used >= d["quantity"]:
            d_idx += 1
            d_used = 0
    else:
        break

print(f"Market Price: {market_price} €/MWh\nMarket Quantity: {market_quantity} MW")

# 5. Plot
colors = {"Company 1": "skyblue", "Company 2": "salmon"}
fig, ax = plt.subplots(figsize=(10, 6))

# Plot Offerta (Barre)
current_x = 0
for bid in supply_bids:
    w, h = bid["effective_capacity"], bid["bid_price"]
    ax.bar(current_x, h, width=w, align='edge', color=colors.get(bid["company"], "gray"), edgecolor='black')
    ax.text(current_x + w/2, h + 2, bid["type"], ha='center', va='bottom', fontsize=9)
    current_x += w

# Plot Domanda (Linea a gradini)
d_x, d_y = [], []
cum_q = 0
for d in demand_bids:
    d_x.extend([cum_q, cum_q + d["quantity"]])
    d_y.extend([d["price"], d["price"]])
    cum_q += d["quantity"]

ax.plot(d_x, d_y, color='orange', linewidth=2.5, label='Domanda Elastica')

# Linee di Market Clearing Point
ax.axvline(x=market_quantity, color='red', linestyle='--')
ax.axhline(y=market_price, color='green', linestyle='--')
ax.set(xlabel="Capacità Cumulativa (MW)", ylabel="Prezzo (€/MWh)", title="Merit Order Curve con Domanda Elastica")

# Legenda
handles = [mpatches.Patch(color=c, label=comp) for comp, c in colors.items()]
handles.append(Line2D([0], [0], color='orange', linewidth=2.5, label='Curva di Domanda'))
handles += [Line2D([0], [0], color='red', linestyle='--'), Line2D([0], [0], color='green', linestyle='--')]
labels = list(colors.keys()) + ['Curva di Domanda', f'Quantità Cleared ({market_quantity} MW)', f'Prezzo Cleared ({market_price} €/MWh)']
ax.legend(handles=handles, labels=labels)

plt.show()