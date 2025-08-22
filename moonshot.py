import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm  # progress bar

# Load historical multipliers
data = pd.read_excel(r"C:\Users\xsimo\OneDrive\Moonshot.xlsx", sheet_name="Data")
historical = data.iloc[:, 0].values

# Load Kelly fractions table
table = pd.read_excel(r"C:\Users\xsimo\OneDrive\Moonshot.xlsx", sheet_name="Table")
table_targets = table.iloc[:, 0].values   # multiplier column
kelly_fractions_table = table.iloc[:, 6].values

# Create a lookup dict for Kelly fractions
kelly_lookup = dict(zip(table_targets, kelly_fractions_table))

# Simulation parameters
rounds = 1000      # reduce for testing, increase later
sims = 50          # reduce for testing, increase later
start_bankroll = 100.0

# Multipliers from 1.00 to 100.00 in steps of 0.01
all_multipliers = np.round(np.arange(1.00, 100.01, 0.01), 2)

results = []

# Use tqdm to show a progress bar
for target in tqdm(all_multipliers, desc="Simulating multipliers"):
    # Use Kelly fraction if available, else 0
    bet_fraction = kelly_lookup.get(target, 0)
    if bet_fraction < 0:
        bet_fraction = 0

    ending_bankrolls = []

    for sim in range(sims):
        bankroll = start_bankroll
        draws = np.random.choice(historical, size=rounds)

        for c in draws:
            if c >= target:
                r = target - 1     # win
            else:
                r = -1             # loss
            bankroll *= (1 + bet_fraction * r)

        ending_bankrolls.append(bankroll)

    ending_bankrolls = np.array(ending_bankrolls)
    results.append({
        "target_multiplier": target,
        "kelly_fraction": bet_fraction,
        "mean_end": ending_bankrolls.mean(),
        "median_end": np.median(ending_bankrolls),
        "risk_of_ruin": (ending_bankrolls < 1).mean()
    })

# Convert to DataFrame
df = pd.DataFrame(results)

# ---- Print top 10 multipliers by median bankroll ----
top10 = df.sort_values("median_end", ascending=False).head(10)
print("Top 10 multipliers by median bankroll:")
print(top10)

# Plot median bankroll vs target multiplier
plt.plot(df["target_multiplier"], df["median_end"])
plt.xlabel("Target Multiplier")
plt.ylabel("Median Ending Bankroll")
plt.title("Median Bankroll vs Target Multiplier (Kelly Fraction Applied)")
plt.yscale('log')
plt.show()