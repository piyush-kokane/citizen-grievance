"""Generate diverse, reproducible synthetic civic-grievance records.

Synthetic data is for pipeline/demo testing, not a substitute for real labelled
complaints. Text is generated from composable patterns with occasional ambiguity,
typos and cross-category wording so the classification task is not trivial.
"""
import random
import sqlite3
from datetime import datetime, timedelta

from database import DATABASE_NAME, create_tables

SEED = 2026
DEPARTMENTS = [
    ("Water Supply", 5),
    ("Roads and Potholes", 7),
    ("Waste Management", 3),
    ("Street Lighting", 5),
    ("Drainage", 4),
    ("Public Health", 7),
    ("Parks and Gardens", 10),
    ("General Administration", 10),
]

ISSUES = {
    "Water Supply": [
        ("tap is dry", "water has not reached our lane", "there is no supply at home"),
        ("the water smells unusual", "muddy water came from the tap", "the supply looks discoloured"),
        ("a pipe is leaking", "water is flowing from a damaged connection", "the valve near our building is broken"),
        ("pressure drops every evening", "supply lasts only a few minutes", "the overhead tank is not filling"),
    ],
    "Roads and Potholes": [
        ("a deep pothole has formed", "the road surface has broken apart", "there are several craters in the lane"),
        ("the road floods after a shower", "loose gravel is spreading across the street", "the surface is uneven near the crossing"),
        ("a manhole cover is missing", "the cover rocks when vehicles pass", "a trench was left open after work"),
        ("vehicles are swerving around the damaged stretch", "two-wheelers skid at this spot", "the school approach is difficult to cross"),
    ],
    "Waste Management": [
        ("the bins have not been emptied", "collection was missed again", "bags are piling up beside the road"),
        ("waste is scattered by animals", "a public bin is overflowing", "rubbish has been left near the shops"),
        ("the collection vehicle skipped our street", "the pickup came much later than usual", "no one collected the bags this week"),
        ("there is a strong smell near the corner", "food waste has remained outside for days", "residents have started dumping rubbish here"),
    ],
    "Street Lighting": [
        ("the lamp goes off after sunset", "the street remains dark at night", "the light near the crossing has failed"),
        ("two lamps keep flickering", "the light switches on and off", "the pole light is very dim"),
        ("a wire is hanging from the lamp post", "the fixture appears damaged", "the light has been out since last week"),
        ("people cannot see the footpath after dark", "the bus stop is poorly lit", "the junction is difficult to navigate at night"),
    ],
    "Drainage": [
        ("the drain is blocked", "dirty water is backing up from the drain", "water is not flowing through the channel"),
        ("sewage has spilled onto the street", "wastewater is entering nearby homes", "there is a foul smell from the manhole"),
        ("rainwater is standing outside the building", "the roadside channel overflows in rain", "water remains pooled for hours"),
        ("the drain cover is broken", "the open channel is a safety risk", "silt has filled the roadside gutter"),
    ],
    "Public Health": [
        ("mosquitoes are increasing around standing water", "residents report repeated insect bites", "there may be a mosquito breeding spot"),
        ("the area has not been sanitised", "a public place is unhygienic", "there is concern about disease spreading"),
        ("stray animals are gathering near the market", "an animal carcass has not been removed", "the public area needs disinfection"),
        ("smoke from burning rubbish is affecting residents", "a strong odour is causing discomfort", "people are worried about sanitation nearby"),
    ],
    "Parks and Gardens": [
        ("the grass is overgrown", "shrubs are blocking the walking path", "the garden needs trimming"),
        ("the play equipment is damaged", "a swing chain has come loose", "the play area looks unsafe"),
        ("benches are broken", "the walking track surface is damaged", "the park gate does not close"),
        ("the garden has not been maintained", "the public lawn is full of weeds", "fallen branches are still on the path"),
    ],
    "General Administration": [
        ("my application has had no update", "a service request is pending", "the office has not responded to my request"),
        ("the details on my certificate are incorrect", "a record needs correction", "the online form shows the wrong information"),
        ("I was sent between counters without an answer", "the required document list is unclear", "the appointment was cancelled without notice"),
        ("the portal will not accept my submission", "I cannot track the request number", "the service has been delayed beyond the promised date"),
    ],
}

OPENERS = [
    "Please look into this:", "Residents of our area report that", "I want to report that",
    "For the past few days,", "Could the municipal team check this?",
    "This has been happening repeatedly:", "Requesting help because",
    "Since last week,", "A neighbour and I noticed that", "Urgent attention requested —",
    "The situation is getting worse:", "Please register a complaint:",
]
LOCATIONS = [
    "near the bus stop", "behind the market", "in Ward {ward}", "by the school gate",
    "near the community hall", "along the main road", "beside building {building}",
    "in our residential lane", "close to the clinic", "at the junction",
    "near the public garden", "on the approach road",
]
ENDINGS = [
    "Please arrange an inspection.", "It is affecting several households.",
    "Kindly resolve it when possible.", "This has been reported before.",
    "Please share an update.", "It is becoming a safety concern.",
    "We have attached no photo yet.", "The issue is still unresolved.",
    "Please forward this to the right team.", "Residents are frustrated.",
    "", "", "",
]
TYPO_MAP = {
    "water": ["water", "water", "watre"],
    "street": ["street", "street", "stret"],
    "please": ["please", "please", "plz"],
    "light": ["light", "light", "lite"],
    "complaint": ["complaint", "complaint", "complnt"],
}

def _make_text(category, rng, ward):
    # Some complaints are vague/incomplete; their assigned category reflects
    # the triage label, but the message alone does not reveal it perfectly.
    # This is intentional and realistic label ambiguity, not random metric noise.
    if rng.random() < 0.20:
        issue = rng.choice([
            "something is wrong and needs attention",
            "the same problem has happened again",
            "the situation has not improved",
            "residents need help with this issue",
            "the request is still pending",
            "please send someone to inspect the area",
            "we are unable to get a clear response",
            "this has become inconvenient for local residents",
        ])
    else:
        issue = rng.choice(rng.choice(ISSUES[category]))
    location = rng.choice(LOCATIONS).format(ward=ward, building=rng.randint(1, 80))
    pieces = [rng.choice(OPENERS), issue, location, rng.choice(ENDINGS)]
    text = " ".join(p for p in pieces if p).strip()
    # Some reports mention a symptom shared by multiple categories. This makes
    # classification less dependent on one unique keyword.
    if rng.random() < 0.22:
        text += " " + rng.choice([
            "and there is a bad smell nearby",
            "people are finding it hard to pass",
            "it gets worse after heavy rain",
            "children and older residents are affected",
            "we have contacted the ward office already",
            "the problem has continued for several days",
        ])
    if rng.random() < 0.12:
        word = rng.choice(list(TYPO_MAP))
        text = text.replace(word, rng.choice(TYPO_MAP[word]), 1)
    if rng.random() < 0.18:
        text = text.lower()
    elif rng.random() < 0.15:
        text = text.upper()
    return text

def generate_data(n_complaints=60000, seed=SEED):
    """Regenerate reference tables and n_complaints diverse synthetic records."""
    rng = random.Random(seed)
    create_tables()
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    for table in (
        "duplicate_pairs", "text_features", "resolutions", "reassignments",
        "status_history", "complaints", "staff", "citizens", "departments", "wards",
    ):
        cursor.execute(f"DELETE FROM {table}")

    cursor.executemany(
        "INSERT INTO wards VALUES (?, ?, ?)",
        [(i, f"Ward {i}", rng.randint(10000, 50000)) for i in range(1, 41)],
    )
    cursor.executemany(
        "INSERT INTO departments VALUES (?, ?, ?)",
        [(i, name, sla) for i, (name, sla) in enumerate(DEPARTMENTS, 1)],
    )
    cursor.executemany(
        "INSERT INTO staff VALUES (?, ?, ?)",
        [(i, f"Staff Member {i}", rng.randint(1, len(DEPARTMENTS))) for i in range(1, 301)],
    )
    cursor.executemany(
        "INSERT INTO citizens VALUES (?, ?, ?)",
        [(i, f"Citizen {i}", rng.randint(1, 40)) for i in range(1, 25001)],
    )

    # Give each ward a distinct underlying service-performance profile. The
    # per-complaint outcomes still vary randomly, but resolution rates should
    # differ meaningfully between wards rather than hovering around one global
    # probability. The range is intentionally broad for dashboard/demo use.
    ward_resolution_rates = {
        ward_id: rng.uniform(0.28, 0.88)
        for ward_id in range(1, 41)
    }

    now = datetime.now().replace(microsecond=0)
    start_date = now - timedelta(days=730)
    duration_seconds = int((now - start_date).total_seconds())
    batch_size = 1000

    for first_id in range(1, n_complaints + 1, batch_size):
        complaints, histories, resolutions = [], [], []
        last_id = min(first_id + batch_size - 1, n_complaints)
        for complaint_id in range(first_id, last_id + 1):
            # Mildly imbalanced categories reflect real service-demand variation.
            department_id = rng.choices(range(1, 9), weights=[14, 17, 15, 9, 13, 10, 8, 14], k=1)[0]
            category = DEPARTMENTS[department_id - 1][0]
            citizen_id = rng.randint(1, 25000)
            ward_id = rng.randint(1, 40)
            complaint_text = _make_text(category, rng, ward_id)
            created_at = start_date + timedelta(seconds=rng.randint(0, duration_seconds))

            # Ward-specific resolution probability creates visible variation
            # in the Ward Scorecard. Non-resolved cases are split between Open
            # and In Progress, with a small ward-specific shift as well.
            resolved_probability = ward_resolution_rates[ward_id]
            remaining = 1.0 - resolved_probability
            in_progress_share = rng.uniform(0.35, 0.65)
            status = rng.choices(
                ["Open", "In Progress", "Resolved"],
                weights=[
                    remaining * (1.0 - in_progress_share),
                    remaining * in_progress_share,
                    resolved_probability,
                ],
                k=1,
            )[0]
            resolved_at = None
            resolution_days = None
            if status == "Resolved":
                resolution_days = round(rng.uniform(0.5, 20), 2)
                resolved_at = created_at + timedelta(days=resolution_days)
                if resolved_at > now:
                    resolved_at = now

            priority = rng.choices(["Low", "Medium", "High"], weights=[28, 48, 24], k=1)[0]
            complaints.append((
                complaint_id, citizen_id, ward_id, department_id, complaint_text,
                category, status, created_at.isoformat(timespec="seconds"),
                resolved_at.isoformat(timespec="seconds") if resolved_at else None, priority,
            ))
            histories.append((complaint_id, None, "Submitted", created_at.isoformat(timespec="seconds")))
            if resolved_at:
                histories.append((complaint_id, "Open", "Resolved", resolved_at.isoformat(timespec="seconds")))
                resolutions.append((complaint_id, rng.choice([
                    "Issue inspected and work completed.", "Repair completed by field team.",
                    "Request reviewed; corrective action recorded.", "Service restored after maintenance.",
                    "Follow-up visit completed.", "Work order closed after verification.",
                ]), resolution_days))

        cursor.executemany("""
            INSERT INTO complaints (
                complaint_id, citizen_id, ward_id, department_id, complaint_text,
                category, status, created_at, resolved_at, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, complaints)
        cursor.executemany("""
            INSERT INTO status_history (complaint_id, old_status, new_status, changed_at)
            VALUES (?, ?, ?, ?)
        """, histories)
        cursor.executemany("""
            INSERT INTO resolutions (complaint_id, resolution_text, resolution_days)
            VALUES (?, ?, ?)
        """, resolutions)
        connection.commit()
        print(f"Generated complaints {first_id} to {last_id}")

    connection.close()
    print(f"Generated {n_complaints:,} diverse synthetic complaints (seed={seed}).")
    print(
        "Ward resolution profiles vary by design "
        f"({min(ward_resolution_rates.values()):.0%}–"
        f"{max(ward_resolution_rates.values()):.0%} target range)."
    )

if __name__ == "__main__":
    generate_data()
