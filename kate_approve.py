#!/usr/bin/env python3
"""
Kate's final approval step. Shows Neil-approved names one at a time.
Approved names are added to approved_names.json and appear on the banner.

Usage:
  python3 kate_approve.py
"""
import os, json

BASE         = os.path.dirname(os.path.abspath(__file__))
PENDING_FILE = os.path.join(BASE, "neil_pending.json")
APPROVED_FILE = os.path.join(BASE, "approved_names.json")

def run():
    if not os.path.exists(PENDING_FILE):
        print("No pending file found. Run neil_review.py first.")
        return

    with open(PENDING_FILE) as f:
        pending = json.load(f)

    neil_approved = [p for p in pending if p["neil_decision"] == "APPROVE"]
    neil_rejected = [p for p in pending if p["neil_decision"] == "REJECT"]

    if not neil_approved:
        print("No Neil-approved names waiting for you.")
        if neil_rejected:
            print(f"Neil rejected {len(neil_rejected)} submission(s) — check neil_pending.json if you want to override.")
        return

    with open(APPROVED_FILE) as f:
        approved = json.load(f)
    existing_names = {a["name"].lower() for a in approved}

    added = []
    skipped = []

    print(f"\n{len(neil_approved)} name(s) passed Neil. Your turn.\n")

    for item in neil_approved:
        name = item["name"]
        note = item.get("note", "")
        submitter = item.get("submitter", "anonymous")

        if name.lower() in existing_names:
            print(f"  '{name}' is already on the banner. Skipping.")
            continue

        print(f"{'─'*50}")
        print(f"  Name:      {name}")
        print(f"  Note:      {note or '(none)'}")
        print(f"  From:      {submitter}")
        print(f"  Neil said: {item['neil_verdict']}")
        choice = input("  Approve? (y/n/skip): ").strip().lower()

        if choice == "y":
            entry = {"name": name}
            if note:
                entry["note"] = note
            approved.append(entry)
            existing_names.add(name.lower())
            added.append(name)
            print(f"  ✓ Added '{name}' to the banner.")
        elif choice == "n":
            skipped.append(name)
            print(f"  ✗ Skipped.")
        else:
            print(f"  — Skipped for now.")

    if added:
        with open(APPROVED_FILE, "w") as f:
            json.dump(approved, f, indent=2)
        print(f"\n{'─'*50}")
        print(f"Added {len(added)} name(s): {', '.join(added)}")
        print("Upload the updated approved_names.json to Netlify to publish.")
    else:
        print("\nNo changes made.")

    # Clear processed items from pending
    remaining = [p for p in pending if p["neil_decision"] == "REJECT" or p["name"] in skipped]
    with open(PENDING_FILE, "w") as f:
        json.dump(remaining, f, indent=2)

if __name__ == "__main__":
    run()
