# COM6008 CW1 - trainer recommendation expert system (v1)
# asks questions then uses forward chaining over the rules to pick a trainer


# questions the system can ask
QUESTIONS = {
    "activity": {
        "text": "What will you mainly use the trainers for?",
        "options": ["running", "gym", "walking", "casual"],
    },
    "surface": {
        "text": "Where do you mostly run?",
        "options": ["road", "trail", "track"],
    },
    "arch": {
        "text": "What is your foot arch like? (wet foot test on paper)",
        "options": ["flat", "normal", "high"],
    },
    "pronation": {
        "text": "Where do your old trainers wear down the most?",
        "options": ["inside", "even", "outside"],
    },
    "mileage": {
        "text": "Roughly how far do you run/walk a week?",
        "options": ["low (under 10 miles)", "medium (10-25 miles)", "high (25+ miles)"],
    },
    "budget": {
        "text": "What is your budget?",
        "options": ["low", "mid", "high"],
    },
}

# inside wear = overpronation, outside = underpronation
PRONATION_MAP = {"inside": "over", "even": "neutral", "outside": "under"}


# knowledge base
# if a condition is a list it means any of those values
RULES = [
    # support and cushioning rules
    {"id": "S1", "if": {"activity": ["running", "walking"], "arch": "flat"},
     "then": ("support", "yes"),
     "because": "flat arches tend to collapse inwards, so extra support helps"},

    {"id": "S2", "if": {"activity": ["running", "walking"], "pronation": "over"},
     "then": ("support", "yes"),
     "because": "overpronation (inside wear) needs a stability shoe"},

    {"id": "S3", "if": {"activity": ["running", "walking"], "arch": ["normal", "high"],
                        "pronation": ["neutral", "under"]},
     "then": ("support", "no"),
     "because": "normal/high arch with no overpronation means a neutral shoe is fine"},

    {"id": "C1", "if": {"activity": ["running", "walking"], "arch": "high"},
     "then": ("cushion", "high"),
     "because": "high arches absorb less shock, so more cushioning is needed"},

    {"id": "C2", "if": {"activity": ["running", "walking"], "pronation": "under"},
     "then": ("cushion", "high"),
     "because": "underpronation puts more impact on the outside of the foot"},

    {"id": "C3", "if": {"activity": ["running", "walking"], "mileage": "high"},
     "then": ("cushion", "high"),
     "because": "high weekly mileage needs a more protective, cushioned shoe"},

    {"id": "C4", "if": {"activity": ["running", "walking"], "arch": ["flat", "normal"],
                        "pronation": ["over", "neutral"], "mileage": ["low", "medium"]},
     "then": ("cushion", "standard"),
     "because": "no high-impact factors, so standard cushioning is enough"},

    # recommendation rules
    {"id": "R1", "if": {"activity": "casual"},
     "then": ("recommendation", "lifestyle trainer (comfort and style over performance)"),
     "because": "casual wear doesn't need technical running features"},

    {"id": "R2", "if": {"activity": "gym"},
     "then": ("recommendation", "cross-training shoe (flat, stable sole for lifting)"),
     "because": "a soft running sole is unstable for lifting and lateral movement"},

    {"id": "R3", "if": {"activity": "running", "surface": "trail", "support": "yes"},
     "then": ("recommendation", "trail running shoe with a wide, stable base"),
     "because": "trail needs grip, and the wider base gives the support needed"},

    {"id": "R4", "if": {"activity": "running", "surface": "trail", "support": "no"},
     "then": ("recommendation", "neutral trail running shoe"),
     "because": "trail needs grip and protection, no extra support needed"},

    {"id": "R5", "if": {"activity": "running", "surface": "track"},
     "then": ("recommendation", "track spikes or lightweight racing flats"),
     "because": "track running is about speed, so light shoes with grip are best"},

    {"id": "R6", "if": {"activity": "running", "surface": "road", "support": "yes", "cushion": "high"},
     "then": ("recommendation", "max-cushion stability running shoe"),
     "because": "needs both support and extra cushioning"},

    {"id": "R7", "if": {"activity": "running", "surface": "road", "support": "yes", "cushion": "standard"},
     "then": ("recommendation", "stability daily running shoe"),
     "because": "needs support but standard cushioning is enough"},

    {"id": "R8", "if": {"activity": "running", "surface": "road", "support": "no", "cushion": "high"},
     "then": ("recommendation", "max-cushion neutral running shoe"),
     "because": "no support needed but extra cushioning helps"},

    {"id": "R9", "if": {"activity": "running", "surface": "road", "support": "no", "cushion": "standard"},
     "then": ("recommendation", "neutral daily running shoe"),
     "because": "no special needs, an all-round neutral shoe works best"},

    {"id": "R10", "if": {"activity": "walking", "support": "yes"},
     "then": ("recommendation", "supportive walking shoe with arch support"),
     "because": "walking all day with support needs puts strain on the arch"},

    {"id": "R11", "if": {"activity": "walking", "support": "no"},
     "then": ("recommendation", "cushioned walking shoe"),
     "because": "comfort is the main priority for walking"},

    # budget
    {"id": "B1", "if": {"budget": "low"},
     "then": ("price", "under £60 - look at last season's models or sale stock"),
     "because": "older models are often the same shoe at a much lower price"},

    {"id": "B2", "if": {"budget": "mid"},
     "then": ("price", "£60-£120 - most mainstream models sit in this range"),
     "because": "this covers most current-season trainers"},

    {"id": "B3", "if": {"budget": "high"},
     "then": ("price", "£120+ - premium foams and newest models"),
     "because": "premium models use lighter, more responsive materials"},
]


def ask(fact):
    question = QUESTIONS[fact]
    print("\n" + question["text"])
    for i, option in enumerate(question["options"], start=1):
        print(f"  {i}. {option}")

    while True:
        choice = input("Enter a number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(question["options"]):
            answer = question["options"][int(choice) - 1]
            break
        print("Invalid choice, try again.")

    # only want the first word e.g. "low (under 10 miles)" -> "low"
    answer = answer.split()[0]

    if fact == "pronation":
        answer = PRONATION_MAP[answer]

    return answer


# inference engine
def condition_met(fact, expected, facts):
    if fact not in facts:
        if fact in QUESTIONS:
            facts[fact] = ask(fact)
        else:
            # not worked out yet
            return False

    if isinstance(expected, list):
        return facts[fact] in expected
    return facts[fact] == expected


def rule_matches(rule, facts):
    # stops at the first false condition so it doesnt ask pointless questions
    for fact, expected in rule["if"].items():
        if not condition_met(fact, expected, facts):
            return False
    return True


def forward_chain():
    facts = {}
    fired = []

    # keep looping until no new rules fire
    new_fact_added = True
    while new_fact_added:
        new_fact_added = False
        for rule in RULES:
            if rule in fired:
                continue
            fact, value = rule["then"]
            if fact in facts:
                continue
            if rule_matches(rule, facts):
                facts[fact] = value
                fired.append(rule)
                new_fact_added = True

    return facts, fired


def main():
    print("=" * 50)
    print("  TRAINER RECOMMENDATION EXPERT SYSTEM")
    print("=" * 50)

    facts, fired = forward_chain()

    print("\n" + "=" * 50)
    if "recommendation" in facts:
        print("Recommended:", facts["recommendation"])
    else:
        print("Sorry, I couldn't find a recommendation for those answers.")
    if "price" in facts:
        print("Price range:", facts["price"])

    # explanation
    show = input("\nDo you want to see how I reached this? (y/n): ").strip().lower()
    if show == "y":
        print("\nReasoning:")
        for rule in fired:
            fact, value = rule["then"]
            print(f"  [{rule['id']}] {fact} = {value}  -> because {rule['because']}")


if __name__ == "__main__":
    main()
