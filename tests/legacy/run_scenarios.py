import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "tests" / "scenarios.json"
BASE_PREFS = ROOT / "user_preferences.json"

def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = merge(out.get(k), v)
        return out
    return b if b is not None else a

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def season_label(item):
    return item.get("sowing", {}).get("season_label")

def categories(recs):
    return [r.get("plant_category") for r in recs]

def validate_invariants(inv, out_json, scenario):
    ok = True
    msgs = []
    recs = out_json.get("recommendations", [])

    def fail(msg):
        nonlocal ok
        ok = False
        msgs.append(" - " + msg)

    if inv.get("all_indoor_ok"):
        for r in recs:
            if not r.get("fit", {}).get("indoor_ok", False):
                fail(f"Expected indoor_ok for all, but {r.get('plant_name')} had indoor_ok={r.get('fit',{}).get('indoor_ok')}")

    if inv.get("all_goal_edible"):
        for r in recs:
            if r.get("plant_category") not in ("herb","vegetable"):
                fail(f"Expected edible only, got {r.get('plant_category')} for {r.get('plant_name')}")

    if inv.get("all_goal_ornamental"):
        for r in recs:
            if r.get("plant_category") in ("vegetable","herb"):
                fail(f"Expected ornamental only, got {r.get('plant_category')} for {r.get('plant_name')}")

    if inv.get("season_now_or_plan_ahead"):
        for r in recs:
            lab = season_label(r)
            if lab not in ("Start now","Plan ahead"):
                fail(f"Unexpected season_label={lab} for {r.get('plant_name')}")

    if inv.get("at_least_one_plan_ahead"):
        if not any(season_label(r) == "Plan ahead" for r in recs):
            fail("Expected at least one 'Plan ahead' item.")

    if inv.get("no_majority_climbers_in_windy"):
        climbers = sum(1 for r in recs if r.get("fit", {}).get("habit") in ("climber","vine","upright"))
        if climbers >= 3:
            fail(f"Windy balcony should penalize climbers; found {climbers}/5 tall/climber-like plants.")

    if inv.get("prefer_container_ok"):
        container_true = sum(1 for r in recs if r.get("fit", {}).get("container_ok"))
        if container_true < 3:
            fail(f"Expected ≥3 container_ok items; got {container_true}")

    if inv.get("favor_full_sun"):
        fullsun = sum(1 for r in recs if r.get("fit", {}).get("sun_need") == "full_sun")
        if fullsun == 0:
            fail("Full-sun case should include some full_sun picks.")

    if inv.get("prefer_color_match_or_fragrant"):
        good = 0
        for r in recs:
            why = " ".join(r.get("why", [])).lower()
            if any(k in why for k in ["purple","white","fragrant","scented","aromatic"]):
                good += 1
        if good < 2:
            fail(f"Expected at least 2 color/fragrance-aligned reasons; got {good}")

    if inv.get("diversity_cap_max2_per_category"):
        cats = categories(recs)
        for c in set(cats):
            if cats.count(c) > 2:
                fail(f"Diversity cap exceeded for {c}: {cats.count(c)} items")

    if inv.get("no_duplicates"):
        seen_keys = set()
        for r in recs:
            sci = (r.get("scientific_name") or "").strip().lower()
            name = (r.get("plant_name") or "").strip().lower()
            key = f"sci:{sci}" if sci else f"name:{name}"
            if key in seen_keys:
                fail(f"Duplicate recommendation detected for {r.get('plant_name')} / {r.get('scientific_name')}")
            seen_keys.add(key)

    if inv.get("different_from_cool_results"):
        # Compare with S2 cool results if present
        baseline_path = ROOT / "tests" / "out_S2_balcony_windy_mixed_smallpots.json"
        if baseline_path.exists():
            baseline = load_json(baseline_path)
            curr_names = {r["plant_name"] for r in recs}
            base_names = {r["plant_name"] for r in baseline.get("recommendations", [])}
            if len(curr_names.symmetric_difference(base_names)) == 0:
                fail("Subtropical override produced identical names to cool scenario; expected differences.")

    return ok, msgs

def main():
    scen = load_json(SCEN)
    meta = scen["meta"]
    suburb = meta["suburb"]
    climate = meta["climate_path"]
    base_prefs = load_json(BASE_PREFS)

    os.makedirs(ROOT / "tests", exist_ok=True)

    failures = 0
    for sc in scen["scenarios"]:
        sid = sc["id"]
        desc = sc["desc"]
        prefs_override = sc.get("prefs_override", {})
        inv = sc.get("invariants", {})
        n = meta.get("n", 5)

        merged_prefs = merge(base_prefs, prefs_override)
        tmp_prefs_path = ROOT / "tests" / f"prefs_{sid}.json"
        save_json(tmp_prefs_path, merged_prefs)

        out_path = ROOT / "tests" / f"out_{sid}.json"

        cli_zone = merged_prefs.get("environment", {}).get("climate_zone")
        cli_args = []
        if cli_zone:
            cli_args = ["--climate-zone", cli_zone]

        cmd = [
            sys.executable, str(ROOT / "main.py"),
            "--suburb", suburb,
            "--n", str(n),
            "--climate", climate,
            "--prefs", str(tmp_prefs_path),
            "--out", str(out_path)
        ] + cli_args

        print(f"\n[{sid}] {desc}")
        print("CMD:", " ".join(cmd))
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode != 0:
            print("STDOUT:\n", r.stdout)
            print("STDERR:\n", r.stderr)
            print(f"FAIL {sid}: process failed")
            failures += 1
            continue

        out_json = load_json(out_path)
        ok, msgs = validate_invariants(inv, out_json, sc)
        if ok:
            print(f"PASS {sid}")
        else:
            print(f"FAIL {sid}")
            for m in msgs:
                print(m)
            failures += 1

    print("\n==== SUMMARY ====")
    if failures == 0:
        print("All scenarios passed.")
        sys.exit(0)
    else:
        print(f"{failures} scenario(s) failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()