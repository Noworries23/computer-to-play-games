import subprocess
from collections import Counter

NUM_RUNS = 100

win_stats = Counter()
tie_count = 0

for i in range(NUM_RUNS):
    print(f"\n========== RUN {i + 1} ==========\n")

    # Run main.py and capture output
    result = subprocess.run(
        ["python", "main.py"],
        capture_output=True,
        text=True
    )

    output = result.stdout
    print(output)  # still show full game output

    # Parse winner from output
    for line in output.splitlines():
        if line.startswith("The winner is player"):
            winner_name = line.replace("The winner is player", "").strip()
            win_stats[winner_name] += 1
            break
        elif line.startswith("The game was a tie"):
            tie_count += 1
            break

# Print summary stats
print("\n========== FINAL STATISTICS ==========")
print(f"Total games: {NUM_RUNS}")

for player, wins in win_stats.items():
    print(f"{player}: {wins} wins")

if tie_count > 0:
    print(f"Ties: {tie_count}")
