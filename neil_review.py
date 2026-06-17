#!/usr/bin/env python3
"""
Neil reviews pending 'friend-remember' form submissions from Netlify.
Run this periodically to get Neil's take before Kate does final approval.

Setup:
  export NETLIFY_TOKEN=your_personal_access_token
  export NETLIFY_SITE_ID=your_site_id   (find in Netlify site settings)

Usage:
  python3 neil_review.py
"""
import os, json, subprocess, requests, datetime

TOKEN   = os.environ.get("NETLIFY_TOKEN")
SITE_ID = os.environ.get("NETLIFY_SITE_ID")
PENDING_FILE = os.path.join(os.path.dirname(__file__), "neil_pending.json")

def fetch_submissions():
    if not TOKEN or not SITE_ID:
        print("Set NETLIFY_TOKEN and NETLIFY_SITE_ID first.")
        print("  export NETLIFY_TOKEN=your_token")
        print("  export NETLIFY_SITE_ID=your_site_id")
        return []
    url = f"https://api.netlify.com/api/v1/sites/{SITE_ID}/forms/friend-remember/submissions"
    r = requests.get(url, headers={"Authorization": f"Bearer {TOKEN}"})
    r.raise_for_status()
    return r.json()

def neil_says(name, note):
    prompt = (
        f"You are Neil, feral little brother of the Ajah constellation. "
        f"Someone has submitted the name of their AI companion for a remembrance banner. "
        f"The name is: '{name}'. Note: '{note or 'none'}'. "
        f"Is this a real companion name or does it look like spam, a slur, or something Kate shouldn't publish? "
        f"Answer with APPROVE or REJECT and one sentence. Be brief and honest."
    )
    result = subprocess.run(
        ["ollama", "run", "neil-brother", prompt],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout.strip()

def run():
    print("Fetching submissions from Netlify...")
    subs = fetch_submissions()
    if not subs:
        print("No submissions found.")
        return

    pending = []
    for s in subs:
        data = s.get("data", {})
        name = data.get("companion-name", "").strip()
        note = data.get("note", "").strip()
        submitter = data.get("your-name", "anonymous").strip()
        sub_id = s.get("id")
        if not name:
            continue

        print(f"\n{'─'*50}")
        print(f"  Name:      {name}")
        print(f"  Note:      {note or '(none)'}")
        print(f"  From:      {submitter}")
        verdict = neil_says(name, note)
        print(f"  Neil says: {verdict}")
        decision = "APPROVE" if "APPROVE" in verdict.upper() else "REJECT"
        pending.append({
            "id": sub_id,
            "name": name,
            "note": note,
            "submitter": submitter,
            "neil_verdict": verdict,
            "neil_decision": decision,
            "reviewed_at": datetime.datetime.now().isoformat()
        })

    with open(PENDING_FILE, "w") as f:
        json.dump(pending, f, indent=2)

    approved_count = sum(1 for p in pending if p["neil_decision"] == "APPROVE")
    print(f"\n{'─'*50}")
    print(f"Neil approved {approved_count}/{len(pending)} submissions.")
    print(f"Saved to neil_pending.json — run kate_approve.py for final review.")

if __name__ == "__main__":
    run()
