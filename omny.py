import csv
import random
import string
from datetime import datetime, timedelta

# -----------------------------------------------------
# Toggle this flag to run quickly while testing.
#   DEBUG = True  → small dataset (~500 riders)
#   DEBUG = False → full-size dataset (~100,000 riders)
# -----------------------------------------------------
DEBUG = True

# ----------------------------------------------------------------------
# Data Generation Functions
# ----------------------------------------------------------------------

def generate_payee_ids(total_ids=100_000, seed=1090):
    random.seed(seed)
    chars = string.ascii_lowercase + string.digits
    ids = {''.join(random.choice(chars) for _ in range(10)) for _ in range(total_ids + 200)}
    return list(ids)[:total_ids]

def simulate_taps(payee_ids, start_date, end_date, avg_trips_per_rider=2.5, seed=1090):
    random.seed(seed)
    total_days = (end_date - start_date).days
    n_taps = int(len(payee_ids) * total_days * avg_trips_per_rider)

    tap_times = [
        start_date + timedelta(
            days=random.uniform(0, total_days),
            hours=random.randint(5, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        for _ in range(n_taps)
    ]

    weighted_payees = random.choices(
        payee_ids,
        weights=[abs(random.normalvariate(0, 1)) for _ in range(len(payee_ids))],
        k=n_taps
    )

    data = list(zip(weighted_payees, tap_times))
    return sorted(data, key=lambda x: x[1])

def apply_capping_policy(tap_data, cap_limit=12, cap_window_days=7, base_fare=2.90):
    paid_trips = {}
    results = []

    for payee, tap_time in tap_data:
        if payee not in paid_trips:
            paid_trips[payee] = []

        window_start = tap_time - timedelta(days=cap_window_days)
        paid_trips[payee] = [t for t in paid_trips[payee] if t >= window_start]

        if len(paid_trips[payee]) < cap_limit:
            fare = base_fare
            paid_trips[payee].append(tap_time)
        else:
            fare = 0.00

        results.append([payee, tap_time, fare])

    return results

def save_to_csv(processed_data, filename="omny_output.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["payee_id", "tap_time", "fare"])
        for payee_id, tap_time, fare in processed_data:
            writer.writerow([payee_id, tap_time.strftime("%Y-%m-%d %H:%M:%S"), f"{fare:.2f}"])


def main():
    START_DATE = datetime(2023, 9, 1)
    END_DATE = datetime(2023, 11, 25)

    # If DEBUG → use smaller values for a fast run:
    if DEBUG:
        total_riders = 50
        avg_trips = 1.0
        print("⚠️ DEBUG MODE: small dataset for testing")
    else:
        total_riders = 100_000
        avg_trips = 2.5

    print("Generating payee IDs...")
    payee_ids = generate_payee_ids(total_ids=total_riders)

    print("Simulating tap data...")
    tap_data = simulate_taps(payee_ids, START_DATE, END_DATE, avg_trips_per_rider=avg_trips)

    print("Applying 7-day fare-capping policy...")
    processed = apply_capping_policy(tap_data)

    # ---- Show one rider’s history ----
    target_payee = processed[0][0]
    rider_history = [row for row in processed if row[0] == target_payee]

    print(f"\nTap history for rider {target_payee}:\n")
    print("{:<6} {:<20} {}".format("Tap #", "Time stamp", "Charge"))
    for idx, (_, t, f) in enumerate(rider_history, start=1):
        print("{:<6} {:<20} ${:.2f}".format(idx, t.strftime("%Y-%m-%d %H:%M:%S"), f))

    # ---- Save full results to CSV ----
    print("\nSaving full dataset to omny_output.csv...")
    save_to_csv(processed)
    print("Done!")

if __name__ == "__main__":
    main()
