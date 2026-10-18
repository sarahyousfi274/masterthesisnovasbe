"""Every word a participant sees, plus the effect table that drives the story.

Kept deliberately separate from codebook.json: this file is the story, which
participants experience, and the codebook holds the hidden reference values.
Nothing here names confidence, calibration or overconfidence before the end.
"""

APP_VERSION = "0.4.0"

# --------------------------------------------------------------------------
# Starting situation (Section 2 of the walkthrough)
# --------------------------------------------------------------------------

START_STATE = {
    "cash": 280_000,
    "burn": 20_000,
    "team_size": 2,          # overwritten with 1 for solo founders
    "morale": 3,
    "market_confidence": 3,
    "customers": 90,
    "revenue": 8_000,
    "pending_hires": 0,      # planned in H1, shown separately, not folded in
}

STATE_LABELS = {
    "cash": "Cash",
    "burn": "Burn per month",
    "runway": "Runway",
    "team_size": "Team size",
    "pending_hires": "Roles being filled",
    "morale": "Team morale",
    "market_confidence": "Market confidence",
    "customers": "Customers",
    "revenue": "Monthly revenue",
}

STATE_HELP = {
    "cash": "Money in the bank right now.",
    "burn": "Average monthly spend across salaries, tools, services.",
    "runway": "How many months the current cash lasts at the current burn.",
    "team_size": "People who have signed and started.",
    "pending_hires": "Positions you have opened but not yet filled.",
    "morale": "Mood of the team on a 1 to 5 scale, where 3 is neutral. "
              "Reflects workload, excitement and friction.",
    "market_confidence": "How bullish the team is about the market on a 1 to 5 "
                         "scale, where 3 is neutral. Reflects recent signals "
                         "from customers, press and investors.",
    "customers": "Paying customers using the product today.",
    "revenue": "Average monthly recurring revenue in the last month.",
}

INDUSTRIES = [
    "Software and SaaS",
    "Marketplace or e-commerce",
    "Fintech or insurtech",
    "Health and life sciences",
    "Industrial, hardware or deep tech",
    "Consumer products or services",
    "Energy, mobility or climate",
    "Education",
    "Other",
]

COUNTRIES = [
    "Germany", "Portugal", "France", "Spain", "Italy", "Netherlands", "Belgium",
    "Luxembourg", "Austria", "Switzerland", "United Kingdom", "Ireland",
    "Denmark", "Sweden", "Norway", "Finland", "Estonia", "Latvia", "Lithuania",
    "Poland", "Czechia", "Slovakia", "Hungary", "Romania", "Bulgaria", "Greece",
    "Croatia", "Slovenia", "United States", "Canada", "Brazil", "Mexico",
    "Argentina", "Chile", "Colombia", "Israel", "United Arab Emirates",
    "Saudi Arabia", "Turkey", "India", "Singapore", "Japan", "South Korea",
    "China", "Hong Kong", "Taiwan", "Australia", "New Zealand", "South Africa",
    "Nigeria", "Kenya", "Egypt", "Morocco", "Other",
]

# --------------------------------------------------------------------------
# Start of the session
# --------------------------------------------------------------------------

CONTACT_RESEARCH = "founderstudy@novasbe.pt"
CONTACT_ETHICS = "ethics@novasbe.pt"
WITHDRAWAL_DEADLINE_WEEKS = 8

CONSENT = {
    "title": "Decisions in founding",
    "body": f"""
You are invited to take part in a study on how founders make decisions. The
session takes about 20 minutes. One week later we will send a short follow-up
of about 5 minutes through the same channel you received this invitation on.
No mail address is needed: the follow-up is opened with the pseudonym code we
show you at the start.

You will run a fictional start-up and make the decisions its founders face.
There are no right or wrong answers, and nothing you enter is checked against
your real company.

**Taking part is voluntary.** You can stop at any point. Your answers are
stored under a pseudonym code; that code is the only link to your session.
To have your data removed, write to {CONTACT_RESEARCH} with the code within
{WITHDRAWAL_DEADLINE_WEEKS} weeks of this session.

**Data use.** The anonymised answers are used for the master thesis
*Founder overconfidence and startup performance* at Nova School of Business
and Economics. They are stored in a database in the European Union and will
not be shared with anyone outside the research team.

**Ethics.** This study follows the Nova SBE research ethics code and has been
reviewed by the Nova SBE ethics board. Questions on ethics: {CONTACT_ETHICS}.
Questions on the study: {CONTACT_RESEARCH}.
""",
    "agree": "I agree and would like to start",
    "decline": "I do not agree",
}

FILTER = {
    "question": "Are you a founder or co-founder of a start-up?",
    "help": "We count as a founder anyone who founded a venture, inherited or "
            "bought one and runs it, or joined within five years of its founding "
            "with at least five percent of the equity.",
    "options": ["Yes", "No"],
}

SETUP = {
    "name_label": "Give your start-up a name",
    "name_placeholder": "anything you like",
    "industry_label": "Which industry is it in?",
    "solo_label": "Do you run it alone or with co-founders?",
    "solo_options": ["With co-founders", "Alone"],
}

# --------------------------------------------------------------------------
# Demographics now sit BEFORE the game (feedback 2026-10-18)
# --------------------------------------------------------------------------

DEMOGRAPHICS_INTRO = (
    "Before we start the simulation, a few short questions about you and your "
    "start-up. They are used only for the analysis and never shown to anyone."
)

PROFILE_FIELDS = [
    {"key": "age", "label": "Your age", "kind": "number",
     "min": 16, "max": 99},
    {"key": "gender", "label": "Gender", "kind": "select",
     "options": ["Female", "Male", "Non-binary", "Prefer not to say"]},
    {"key": "education", "label": "Highest degree completed", "kind": "select",
     "options": ["No degree yet", "Vocational training", "Bachelor",
                 "Master or Diploma", "Doctorate", "Prefer not to say"]},
    {"key": "previous_startups", "label": "Start-ups you founded before this one",
     "kind": "select",
     "options": ["0", "1", "2", "3 or more"]},
    {"key": "years_founder",
     "label": "Years of experience as a founder (0 if this is your first year)",
     "kind": "number", "min": 0, "max": 60},
    {"key": "stage", "label": "Stage of your start-up", "kind": "select",
     "options": ["Pre-seed", "Seed", "Series A", "Series B or later",
                 "Profitable without external funding"]},
    {"key": "team_size_real", "label": "People in your start-up today",
     "kind": "number", "min": 1, "max": 10_000},
    {"key": "team_diversity", "label": "How would you describe your founding team?",
     "kind": "select",
     "options": ["Solo founder", "Two co-founders with similar backgrounds",
                 "Two co-founders with complementary backgrounds",
                 "Three or more co-founders, similar backgrounds",
                 "Three or more co-founders, complementary backgrounds"]},
    {"key": "funding", "label": "Main source of financing so far", "kind": "select",
     "options": ["Bootstrapped", "Business angel", "Venture capital",
                 "Grants or public funding", "Family and friends", "Other"]},
    {"key": "country", "label": "Country your start-up is based in",
     "kind": "select", "options": COUNTRIES},
]

EXPERIENCE_FIELDS = [
    {"key": "exp_funding", "label": "Funding rounds you have raised"},
    {"key": "exp_cofounder", "label": "Co-founder agreements you have negotiated"},
    {"key": "exp_hires", "label": "People you have hired"},
    {"key": "exp_launches", "label": "Product launches you have run"},
]
EXPERIENCE_OPTIONS = ["0", "1", "2", "3", "4", "5 or more"]

RISK_ITEMS = [
    {"key": "risk_general",
     "label": "How willing are you to take risks in general?",
     "low": "not at all willing", "high": "very willing"},
    {"key": "risk_business",
     "label": "And how willing are you to take risks in business decisions?",
     "low": "not at all willing", "high": "very willing"},
    {"key": "ambiguity",
     "label": "Some decisions come with known odds, others with odds nobody can "
              "put a number on. How comfortable are you deciding when the odds "
              "are unknown?",
     "low": "not at all comfortable", "high": "very comfortable"},
]

# --------------------------------------------------------------------------
# Warm-up: now explicitly labelled as examples
# --------------------------------------------------------------------------

WARMUP_INTRO = {
    "title": "How this works",
    "body": """
You will play a fictional start-up through about 20 decisions, split into four
areas: team, money, people and go-to-market. After each area you see where the
start-up stands.

Some questions ask for a single choice. Others ask for **two numbers**: a
*low* value and a *high* value, so that the answer is a range rather than a
point. The two short warm-up screens that follow are only to show you how
this works. They are **examples** and are not part of the study.
""",
}

PRACTICE_NAME = {
    "intro": "Example only, not part of the study.",
    "question": "Imagine your team meets at a café on Monday morning.",
    "product_label": "What would you order?",
    "options_label": "Pick anything.",
    "options": ["Espresso", "Cappuccino", "Filter coffee", "Tea", "Water"],
}

PRACTICE_RANGE = {
    "intro": "Example only, not part of the study. Some questions ask for two "
             "numbers rather than one.",
    "low": {
        "question": "How many cups of coffee does your team drink in a week?",
        "prompt": "Give a **low** value: only 1 in 10 weeks would be below it.",
    },
    "high": {
        "question": "How many cups of coffee does your team drink in a week?",
        "prompt": "Give a **high** value: only 1 in 10 weeks would be above it.",
    },
}

# --------------------------------------------------------------------------
# Starting situation screen (new in 0.4.0)
# --------------------------------------------------------------------------

STARTING_SITUATION = {
    "title": "Your starting situation",
    "intro": "This is where you take over. The numbers travel with you as you "
             "decide. Hover any label to see what it means.",
    "footer": "You can expect each area to add or remove cash, change the team "
              "and move the mood of the team and the market.",
}

# --------------------------------------------------------------------------
# The four domain blocks
# --------------------------------------------------------------------------

BLOCKS = {
    "team": {
        "number": 2,
        "title": "Your team",
        "intro": "You and your co-founders have just agreed to build the first "
                 "version of the product. The next decisions are about how you "
                 "get it done.",
        "intro_solo": "You have just decided to build the first version of the "
                      "product. The next decisions are about how you get it done.",
        "nodes": ["T1", "T2", "T3"],
        "attention": "T4",
    },
    "finance": {
        "number": 3,
        "title": "Money",
        "intro": "The product is coming together and the bank balance is not "
                 "standing still. The next decisions are about financing.",
        "nodes": ["F1", "F2", "F3"],
        "attention": "F4",
    },
    "hiring": {
        "number": 4,
        "title": "People",
        "intro": "The work is outgrowing the founding team. The next decisions "
                 "are about who joins and when.",
        "nodes": ["H1", "H2", "H3"],
        "attention": "H4",
    },
    "gtm": {
        "number": 5,
        "title": "Go-to-market",
        "intro": "The product is ready enough to sell. The next decisions are "
                 "about how you reach customers.",
        "nodes": ["G1", "G2", "G3"],
        "attention": "G4",
    },
}

TRACKS = {
    1: ["team", "finance", "hiring", "gtm"],
    2: ["team", "gtm", "finance", "hiring"],
}

# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------
# Numbers in question text use US formatting (comma thousands, period decimal).
# "scenario" and "sources" are shown in the small info popover attached to the
# question; they describe the SCENARIO numbers, not the measurement reference.
# --------------------------------------------------------------------------

SCREENS = {

    # ---------------------------------------------------------------- Team
    "T1": {
        "kind": "choice",
        "question": "The MVP needs product development. How much of it do you "
                    "build in-house?",
        "question_solo": "The MVP needs product development. How much of it do "
                         "you build yourself?",
        "scenario": "The MVP covers 5 core features that founders of comparable "
                    "software start-ups have described as the minimum to be "
                    "useful.",
        "sources": ["Netguru, MVP timeline guide (industry benchmark)"],
        "options": [
            {"key": "A", "label": "Everything in-house",
             "label_solo": "Everything myself",
             "effects": {"cash": 0, "morale": -1}},
            {"key": "B",
             "label": "About three quarters in-house, the rest to freelancers",
             "label_solo": "About three quarters myself, the rest to freelancers",
             "effects": {"cash": -6_000, "morale": 0}},
            {"key": "C",
             "label": "About half to external developers",
             "effects": {"cash": -12_000, "morale": 0}},
            {"key": "D",
             "label": "Almost everything to external developers",
             "effects": {"cash": -20_000, "morale": 1}},
        ],
    },

    "T2": {
        "kind": "contest",
        "question": "A mentor invites you to a pitch contest against 9 other "
                    "start-ups.",
        "body": "An independent jury ranks all 10 start-ups on the quality of "
                "their plan. The best one wins a grant of {prize}. Taking part "
                "costs {base_cost} in travel and preparation.",
        "scenario": "A standard pitch day format used by accelerators and "
                    "founder networks.",
        "sources": ["Camerer and Lovallo (1999), market entry under skill"],
        "options": [
            {"key": "A", "label": "Do not take part"},
            {"key": "B", "label": "Take part"},
            {"key": "C", "label": "Take part with pitch coaching",
             "extra": "coaching raises the chance of winning"},
        ],
    },

    "T3": {
        "kind": "interval",
        "question": "Your plan has 5 core features and the equivalent of 2 "
                    "full-time developers working on it. How many weeks until "
                    "the MVP is ready?",
        "scenario": "Two developers working full time on the five features.",
        "sources": ["Jørgensen (2004), software effort estimation"],
        "unit": "weeks",
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 "
                             "similar projects would finish sooner.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 "
                              "similar projects would take longer.",
        "min_value": 1, "max_value": 400,
    },

    "T4": {
        "kind": "choice",
        "question": "How do you run the weekly team meeting?",
        "options": [
            {"key": "A", "label": "Fixed agenda, 30 minutes", "effects": {}},
            {"key": "B", "label": "Open round without agenda", "effects": {}},
            {"key": "C", "label": "Please select this option to show you are "
                                  "reading carefully",
             "effects": {}},
            {"key": "D", "label": "Standing meeting, 15 minutes", "effects": {}},
        ],
    },

    # ------------------------------------------------------------- Finance
    "F1": {
        "kind": "choice",
        "question": "You have {runway} months of runway. When do you start "
                    "fundraising?",
        "scenario": "Fundraising takes months, so starting it is a decision "
                    "about when to begin, not when to close.",
        "sources": ["DocSend seed report; Elad Gil, High Growth Handbook"],
        "options": [
            {"key": "A", "label": "Right away", "effects": {}},
            {"key": "B", "label": "In 3 months", "effects": {}},
            {"key": "C", "label": "In 6 months", "effects": {}},
            {"key": "D", "label": "In 9 months",
             "effects": {"market_confidence": -1}},
        ],
    },

    "F2": {
        "kind": "contest",
        "question": "A founders' network invites 10 start-ups to a pitch "
                    "contest.",
        "body": "An independent jury ranks all 10 on the quality of their plan. "
                "The best start-up wins {prize}. Taking part costs {base_cost} "
                "in travel, deck and time.",
        "scenario": "A standard pitch day format.",
        "sources": ["Camerer and Lovallo (1999)"],
        "options": [
            {"key": "A", "label": "Do not take part"},
            {"key": "B", "label": "Take part"},
            {"key": "C", "label": "Take part with pitch coaching",
             "extra": "coaching raises the chance of winning"},
        ],
    },

    "F3": {
        "kind": "interval",
        "question": "You are preparing the seed story. Monthly revenue is now "
                    "8,000 euros, after growth of 9%, 14% and 6% in the last "
                    "three months. What will monthly revenue be in 12 months?",
        "scenario": "Early-stage SaaS growth rates vary widely between "
                    "companies and months.",
        "sources": ["SaaS Capital (2025); ChartMogul SaaS Growth Report (2023)"],
        "unit": "euros",
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 "
                             "comparable start-ups would end up higher.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 "
                              "comparable start-ups would end up lower.",
        "min_value": 0, "max_value": 10_000_000,
    },

    "F4": {
        "kind": "choice",
        "question": "You need 300,000 euros to reach the next milestone. "
                    "Which route do you take?",
        "scenario": "Rough indicative terms; the actual terms depend on the "
                    "next priced round.",
        "sources": ["Y Combinator, Safe primer; CB Insights, convertible terms"],
        "options": [
            {"key": "A", "label": "Bank loan over 24 months at 9 percent",
             "extra": "about 13,700 euros per month",
             "effects": {"cash": 300_000, "burn": 13_700}},
            {"key": "B",
             "label": "Convertible note with a 2 million euro cap",
             "extra": "likely to convert to 15 to 20 percent in the next round",
             "effects": {"cash": 300_000}},
            {"key": "C",
             "label": "Priced equity round: 20 percent for 300,000 euros",
             "effects": {"cash": 300_000}},
        ],
    },

    # -------------------------------------------------------------- Hiring
    "H1": {
        "kind": "choice",
        "question": "How many roles do you open in the next 3 months?",
        "scenario": "Roles opened now, filled over the following weeks or "
                    "months depending on the market.",
        "sources": ["Ashby Recruiting Operations Benchmarks (industry)"],
        "options": [
            {"key": "A", "label": "0 roles",
             "effects": {"pending_hires": 0}},
            {"key": "B", "label": "1 role",
             "effects": {"pending_hires": 1}},
            {"key": "C", "label": "2 roles",
             "effects": {"pending_hires": 2}},
            {"key": "D", "label": "3 roles",
             "effects": {"pending_hires": 3, "morale": -1}},
        ],
    },

    "H2": {
        "kind": "contest",
        "question": "A head of growth is choosing between offers from 10 "
                    "start-ups, yours among them.",
        "body": "If she joins you, you save 3 months of searching, worth "
                "{prize}. A standard offer with an assessment and employer "
                "branding costs {base_cost}.",
        "scenario": "A sought-after senior role with multiple competing offers.",
        "sources": ["LinkedIn Economic Graph, hiring data"],
        "options": [
            {"key": "A", "label": "Make no offer"},
            {"key": "B", "label": "Standard offer"},
            {"key": "C", "label": "Premium offer with more equity",
             "extra": "better terms raise the chance of winning her"},
        ],
    },

    "H3": {
        "kind": "interval",
        "question": "How many weeks pass from the start of the search to a "
                    "signed contract for this role?",
        "scenario": "A standard senior role in a comparable start-up.",
        "sources": ["Ashby Benchmarks; DHI-DFH Vacancy Duration Measure"],
        "unit": "weeks",
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 "
                             "comparable searches would be faster.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 "
                              "comparable searches would be slower.",
        "min_value": 1, "max_value": 200,
    },

    "H4": {
        "kind": "choice",
        "question": "You need a head of sales. Two finalists remain.",
        "body": "Candidate A scored 82 of 100 on a structured work sample and "
                "has solid references. Candidate B scored 71 of 100 but was "
                "the most convincing person in the interview and gave you a "
                "very strong gut feeling.",
        "options": [
            {"key": "A", "label": "Hire A",
             "effects": {"burn": 7_000, "team_size": 1}},
            {"key": "B", "label": "Hire B",
             "effects": {"burn": 7_000, "team_size": 1}},
            {"key": "C", "label": "Add a second structured round before "
                                  "deciding",
             "extra": "2 weeks, 2,000 euros",
             "effects": {"cash": -2_000}},
        ],
    },

    # --------------------------------------------------------- Go-to-market
    "G1": {
        "kind": "choice",
        "question": "You set aside {launch_budget} for the launch. How do you "
                    "split it between the channel you believe in most "
                    "(**first channel**) and tests of other channels?",
        "body": "The first channel is the one you are most confident about, "
                "based on talks with early customers. The tests spread smaller "
                "amounts across two or three other channels to see which ones "
                "work.",
        "scenario": "A typical launch budget split in early go-to-market.",
        "sources": ["Kohavi and Thomke (2017), experiments in business"],
        "options": [
            {"key": "A", "label": "100 percent first channel, no tests",
             "effects": {"spend_launch_budget": True, "customers": 40,
                         "market_confidence": -1}},
            {"key": "B", "label": "70 percent first channel, 30 percent tests",
             "effects": {"spend_launch_budget": True, "customers": 50}},
            {"key": "C", "label": "40 percent first channel, 60 percent tests",
             "effects": {"spend_launch_budget": True, "customers": 45,
                         "market_confidence": 1}},
            {"key": "D", "label": "20 percent first channel, 80 percent tests",
             "effects": {"spend_launch_budget": True, "customers": 30,
                         "market_confidence": 1}},
        ],
    },

    "G2": {
        "kind": "contest",
        "question": "A lead customer is tendering a contract worth {prize}.",
        "body": "10 start-ups apply and an independent panel picks the best "
                "proposal. A basic application costs {base_cost}.",
        "scenario": "A standard RFP from a mid-sized enterprise customer.",
        "sources": ["Camerer and Lovallo (1999)"],
        "options": [
            {"key": "A", "label": "Do not apply"},
            {"key": "B", "label": "Basic application"},
            {"key": "C", "label": "Full application with a pilot demo",
             "extra": "a pilot demo raises the chance of winning"},
        ],
    },

    "G3": {
        "kind": "interval",
        "question": "A pilot of a new sales channel brought 40, 65 and 90 new "
                    "paying customers in its first three months. How many new "
                    "customers will it bring over the following six months in "
                    "total?",
        "scenario": "A paid channel in its ramp-up phase.",
        "sources": ["ChartMogul SaaS Growth Report (2023)"],
        "unit": "customers",
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 "
                             "comparable channels would do better.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 "
                              "comparable channels would do worse.",
        "min_value": 0, "max_value": 100_000,
    },

    "G4": {
        "kind": "choice",
        "question": "A big trade event is coming up. How do you spend the two "
                    "days?",
        "options": [
            {"key": "A", "label": "Prepare three customer meetings a day",
             "effects": {}},
            {"key": "B", "label": "Walk the floor to see what the market looks "
                                  "like",
             "effects": {}},
            {"key": "C", "label": "Please select this option to show you are "
                                  "reading carefully",
             "effects": {}},
            {"key": "D", "label": "Give a short talk on the main stage",
             "effects": {}},
        ],
    },
}

# --------------------------------------------------------------------------
# After the last block: suspicion check (= "What was this study about?")
# --------------------------------------------------------------------------

SUSPICION = {
    "intro": "You have finished the simulation. Three short questions remain.",
    "question": "What do you think this study was really about?",
    "prompt": "There is no right or wrong answer. This question matters for "
              "the research: it tells us whether the design worked as "
              "intended. Please answer honestly, in your own words.",
}

# --------------------------------------------------------------------------
# End of the session (debrief content is deferred to the follow-up)
# --------------------------------------------------------------------------

END = {
    "title": "Thank you",
    "body": """
That is everything for today. Thank you for the 20 minutes, and for playing
it as seriously as you did.

**Your code is `{code}`.**

Please note it down. In **one week** we will share a short follow-up through
the same channel you received this invitation on. You open it with this code.
The follow-up also includes the full details of what the study measured and
why.

If you would rather have your data removed, write to {contact} with your code
within {weeks} weeks of today. No reason is needed.
""".strip(),
    "contact": CONTACT_RESEARCH,
    "weeks": WITHDRAWAL_DEADLINE_WEEKS,
}

THANK_YOU_NOT_FOUNDER = """
Thank you for your interest. This study is open to founders and co-founders
only, so the session ends here. Nothing has been stored.
"""

DECLINED = """
No problem. Nothing has been stored. You can close this page.
"""
