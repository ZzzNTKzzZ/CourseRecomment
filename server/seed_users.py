"""
seed_users.py  (CSV-only edition)
─────────────────────────────────────────────────────────────────────────────
Generates synthetic users and writes them DIRECTLY to users.csv.
No HTTP calls. No server dependency. Runs in seconds, not hours.

The server (server.py) pre-loads users.csv at startup automatically.

Usage:
    python seed_users.py              # generate up to END_USER
    python seed_users.py --fresh      # delete existing file and start over

users.csv columns:
  user_id, interests, num_enrolled, num_rated,
  enrolled_course_indices, enrolled_course_names,
  ratings  (format: "idx:stars|idx:stars|…")
"""

import csv
import os
import random
import sys
import time
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
CSV_FILE = "Coursera.csv"
OUT_CSV  = "users.csv"
END_USER = 1000        # total users to generate (1 … END_USER)
SEED     = 42

random.seed(SEED)

# ── Optional: --fresh flag wipes existing file ────────────────────────────────
if "--fresh" in sys.argv:
    if os.path.exists(OUT_CSV):
        os.remove(OUT_CSV)
        print(f"Deleted existing {OUT_CSV}")

# ── Auto-detect last existing user from users.csv ─────────────────────────────
def detect_start_user(filepath: str) -> int:
    """Returns next user number to generate (max existing + 1, or 1)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return 1
        last_num = max(
            int(row["user_id"].rsplit("_", 1)[-1])
            for row in rows
            if row["user_id"].rsplit("_", 1)[-1].isdigit()
        )
        return last_num + 1
    except FileNotFoundError:
        return 1

START_USER = detect_start_user(OUT_CSV)
NUM_USERS  = max(0, END_USER - START_USER + 1)

# ── Name pools ────────────────────────────────────────────────────────────────
FIRST = [
    "alice","bob","carol","dave","eve","frank","grace","hank","iris","jack",
    "kate","leo","mia","noah","olivia","peter","quinn","rosa","sam","tara",
    "umar","vera","will","xena","yuki","zara","aiden","bella","cam","diana",
    "eli","fiona","george","hana","ivan","julia","kyle","luna","mike","nina",
    "omar","penny","ray","sofia","tom","uma","vince","wendy","xiao","yan",
]
DOMAINS = ["dev","ml","biz","edu","pro","ai","labs","hub","io","xyz"]

def random_username(i: int) -> str:
    return f"{random.choice(FIRST)}_{random.choice(DOMAINS)}_{i}"

# ── Load Coursera.csv ─────────────────────────────────────────────────────────
print(f"Loading courses from {CSV_FILE} ...")
with open(CSV_FILE, encoding="utf-8") as f:
    courses = list(csv.DictReader(f))
print(f"   -> {len(courses)} courses loaded")

# ── Build topic index ─────────────────────────────────────────────────────────
STOP = {
    "and","the","of","a","in","to","for","with","on","by","or","is","are",
    "be","it","as","an","at","this","that","from","was","not","but","we",
    "you","your","our","their","its","course","courses","learn","learning"
}

def keywords(course: dict) -> list:
    raw = course.get("Skills","") + " " + course.get("Difficulty Level","")
    tokens = [w.strip().lower() for w in raw.replace("  "," ").split()]
    return [t for t in tokens if t and t not in STOP and len(t) > 3]

topic_index    = defaultdict(list)
course_keywords = []

for idx, c in enumerate(courses):
    kws = keywords(c)
    course_keywords.append(kws)
    for kw in set(kws):
        topic_index[kw].append(idx)

topic_freq = {kw: len(idxs) for kw, idxs in topic_index.items()}
TOP_TOPICS = [kw for kw, _ in
              sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:200]]
print(f"   -> {len(TOP_TOPICS)} interest topics identified")

# ── Guard: nothing to do? ─────────────────────────────────────────────────────
if NUM_USERS <= 0:
    print(f"\nusers.csv already complete (users up to #{START_USER - 1}). "
          f"Use --fresh to regenerate, or raise END_USER (currently {END_USER}).")
    raise SystemExit(0)

print(f"\nGenerating {NUM_USERS} users (#{START_USER} to #{END_USER}) -> {OUT_CSV}\n")

# ── CSV output columns ────────────────────────────────────────────────────────
CSV_COLUMNS = [
    "user_id",
    "interests",
    "num_enrolled",
    "num_rated",
    "enrolled_course_indices",
    "enrolled_course_names",
    "ratings",
]

# Append if file already has data; write fresh (with header) otherwise
file_exists = os.path.isfile(OUT_CSV) and os.path.getsize(OUT_CSV) > 0
open_mode   = "a" if file_exists else "w"

total_enrollments = 0
total_ratings     = 0
start             = time.time()

with open(OUT_CSV, open_mode, newline="", encoding="utf-8") as out_f:
    writer = csv.DictWriter(out_f, fieldnames=CSV_COLUMNS)
    if not file_exists:
        writer.writeheader()

    for i in range(START_USER, END_USER + 1):
        username = random_username(i)

        # Pick 1–3 interest clusters
        num_interests  = random.randint(1, 3)
        user_interests = random.sample(TOP_TOPICS, num_interests)

        # Build candidate pool
        candidate_set = set()
        for interest in user_interests:
            for idx in topic_index.get(interest, []):
                candidate_set.add(idx)
        for _ in range(random.randint(1, 3)):
            candidate_set.add(random.randint(0, len(courses) - 1))

        candidates = list(candidate_set)
        num_enroll = min(random.randint(5, 20), len(candidates))
        enrolled   = random.sample(candidates, num_enroll)
        total_enrollments += len(enrolled)

        # Rate 40–80 % of enrolled courses
        num_to_rate   = max(1, int(len(enrolled) * random.uniform(0.4, 0.8)))
        courses_rated = random.sample(enrolled, num_to_rate)
        rating_map    = {}

        for course_idx in courses_rated:
            c_kws   = set(course_keywords[course_idx])
            overlap = len(c_kws & set(user_interests))

            if overlap > 0:
                rating = random.choices([3, 4, 5], weights=[15, 35, 50])[0]
            else:
                rating = random.choices([1, 2, 3, 4], weights=[15, 25, 35, 25])[0]

            rating_map[course_idx] = rating

        total_ratings += len(rating_map)

        # Write row — NO HTTP calls needed
        enrolled_names = [courses[idx].get("Course Name","Unknown") for idx in enrolled]
        ratings_str    = "|".join(f"{idx}:{r}" for idx, r in rating_map.items())

        writer.writerow({
            "user_id"                : username,
            "interests"              : "|".join(user_interests),
            "num_enrolled"           : len(enrolled),
            "num_rated"              : len(rating_map),
            "enrolled_course_indices": "|".join(str(idx) for idx in enrolled),
            "enrolled_course_names"  : "|".join(enrolled_names),
            "ratings"                : ratings_str,
        })

        # Progress every 100 users
        if i % 100 == 0 or i == END_USER:
            elapsed = time.time() - start
            pct     = (i - START_USER + 1) / NUM_USERS * 100
            filled  = int(30 * (i - START_USER + 1) // NUM_USERS)
            bar     = "#" * filled + "-" * (30 - filled)
            print(f"  [{bar}] {pct:5.1f}%  user {i:>4}/{END_USER}"
                  f"  enrollments={total_enrollments:>7}"
                  f"  ratings={total_ratings:>7}"
                  f"  elapsed={elapsed:>5.1f}s",
                  flush=True)

elapsed = time.time() - start
print(f"""
+--------------------------------------------------+
|   CSV-only seeding complete!                     |
+--------------------------------------------------+
|  Users generated   : {NUM_USERS:<28}|
|  Total enrollments : {total_enrollments:<28}|
|  Total ratings     : {total_ratings:<28}|
|  Time elapsed      : {elapsed:<25.2f}s |
|  Output file       : {OUT_CSV:<28}|
+--------------------------------------------------+
Restart server.py to reload users.csv automatically.
""")
