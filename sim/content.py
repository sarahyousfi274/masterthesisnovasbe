"""Every word a participant sees, plus the effect table that drives the story.

Kept deliberately separate from codebook.json: this file is the story, which
participants experience, and the codebook holds the hidden reference values.
Nothing here names confidence, calibration or overconfidence, and the scenario
popovers cite only the data sources behind the scenario numbers, never the
research on judgement that the study builds on.
"""

APP_VERSION = "0.6.0"

# --------------------------------------------------------------------------
# Contact details. Replace the study address once the team mailbox exists.
# --------------------------------------------------------------------------

CONTACT_EMAIL = "[study email]"
WITHDRAWAL_WEEKS = 4

# --------------------------------------------------------------------------
# Starting situation
# --------------------------------------------------------------------------

START_STATE = {
    "cash": 280_000,
    "burn": 20_000,
    "team_size": 2,          # overwritten with 1 for solo founders
    "pending_hires": 0,      # roles opened in H1, shown separately
    "morale": 3,
    "market_confidence": 3,
    "customers": 90,
    "revenue": 8_000,
}

STATUS_FIELDS = [
    # key, label, help text
    ("cash", "Cash", "Money in the bank right now."),
    ("burn", "Burn per month", "What the startup spends each month on salaries, "
                               "tools, rent and services."),
    ("runway", "Runway", "How many months the cash lasts at the current burn. "
                         "Cash divided by burn per month."),
    ("team_size", "Team", "People working in the startup, founders "
                          "included."),
    ("pending_hires", "Open roles", "Positions you have opened but not filled "
                                    "yet. They count toward the team once "
                                    "someone signs."),
    ("customers", "Customers", "Paying customers using the product today."),
    ("morale", "Team morale", "Mood of the team, from 1 (very low) to 5 (very "
                              "high). 3 is neutral."),
    ("market_confidence", "Market confidence", "How positive the signals from "
                                               "customers, press and investors "
                                               "are, from 1 (very low) to 5 "
                                               "(very high). 3 is neutral."),
]

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
# Sections shown in the bar at the top
# --------------------------------------------------------------------------

SECTION_ABOUT = "About you"
SECTION_HOW = "How it works"
SECTION_STARTUP = "Your startup"
SECTION_WRAP = "Wrap-up"

# --------------------------------------------------------------------------
# Welcome and consent
# --------------------------------------------------------------------------

CONSENT = {
    "title": "Decisions in founding",
    "lead": "A simulation study for founders, run by master’s students at Nova "
            "School of Business and Economics.",
    "facts": [
        ("About 20 minutes", "One sitting, on any device"),
        ("A fictional startup", "No right or wrong answers"),
        ("A 5-minute follow-up", "By email, one week later"),
    ],
    "sections": [
        ("What you will do",
         "You run a fictional startup and make the decisions its founders face. "
         "Nothing you enter is checked against your real company."),
        ("Taking part is voluntary",
         f"You can have your data removed within {WITHDRAWAL_WEEKS} weeks by "
         f"writing to {CONTACT_EMAIL}. No reason is needed."),
        ("Your data",
         "Your email address is stored separately from your answers. The answers "
         "are analyzed only in aggregate, used only for this research project and "
         "never shared outside the research team."),
        ("Ethics",
         "This study follows the research ethics guidelines of Nova School of "
         "Business and Economics."),
    ],
    "agree": "I agree, let’s start",
    "decline": "I do not agree",
}

FILTER = {
    "question": "Have you founded or co-founded a company?",
    "help": "Current or past, any size and any industry. Joining a company early "
            "with a meaningful share of the equity counts too.",
    "options": ["Yes", "No"],
}

EMAIL = {
    "question": "Your email address",
    "body": "We use it for one thing only: to send you the short follow-up in "
            "one week. It is stored separately from your answers and never "
            "shared.",
    "label": "Email",
    "placeholder": "you@company.com",
}

# --------------------------------------------------------------------------
# About you (not part of the simulation)
# --------------------------------------------------------------------------

ABOUT_NOTE = "This part is about you, not the simulation."

PROFILE = {
    "question": "About you and your startup",
    "body": "A few questions for the analysis. If you no longer run a company, "
            "answer for the most recent one. Your answers are never published "
            "individually.",
}

PROFILE_FIELDS = [
    {"key": "age", "label": "Your age", "kind": "number", "min": 16, "max": 99,
     "col": 0},
    {"key": "gender", "label": "Gender", "kind": "select", "col": 1,
     "options": ["Female", "Male", "Non-binary", "Prefer not to say"]},
    {"key": "education", "label": "Highest degree completed", "kind": "select",
     "col": 0,
     "options": ["No formal degree", "High school diploma", "Apprenticeship",
                 "Bachelor’s degree", "Master’s degree or Diploma", "Doctorate",
                 "Prefer not to say"]},
    {"key": "country", "label": "Country your startup is based in",
     "kind": "select", "options": COUNTRIES, "col": 1},
    {"key": "previous_startups", "label": "Startups you founded before this one",
     "kind": "pills", "options": ["0", "1", "2", "3 or more"]},
    {"key": "years_founder",
     "label": "Years of experience as a founder (0 if this is your first year)",
     "kind": "number", "min": 0, "max": 60, "col": 0},
    {"key": "employees",
     "label": "People employed in your startup, not counting the founders",
     "kind": "number", "min": 0, "max": 100_000, "col": 1},
    {"key": "stage", "label": "Stage of your startup", "kind": "select",
     "options": ["Idea", "Pre-seed", "Seed", "Series A", "Series B or later"]},
    {"key": "team_composition", "label": "How would you describe your founding team?",
     "kind": "select",
     "options": ["Solo founder", "Two co-founders with similar backgrounds",
                 "Two co-founders with complementary backgrounds",
                 "Three or more co-founders with similar backgrounds",
                 "Three or more co-founders with complementary backgrounds"]},
    {"key": "funding", "label": "Sources of financing so far (select all that apply)",
     "kind": "multi",
     "options": ["Own savings", "Revenue", "Family and friends",
                 "Business angels", "Venture capital", "Grants or public funding",
                 "Bank loan", "Other"]},
]

EXPERIENCE = {
    "question": "How much of this have you done before?",
    "body": "Count everything across your career, not only this startup.",
}
EXPERIENCE_FIELDS = [
    {"key": "exp_funding", "label": "Funding rounds you have raised"},
    {"key": "exp_cofounder", "label": "Co-founder agreements you have negotiated"},
    {"key": "exp_hires", "label": "People you have hired"},
    {"key": "exp_launches", "label": "Product launches you have run"},
]
EXPERIENCE_OPTIONS = ["0", "1", "2", "3", "4", "5 or more"]

RISK = {
    "question": "How you decide",
    "body": "Three questions about your general attitude. Pick a point on each "
            "scale.",
}
RISK_ITEMS = [
    {"key": "risk_general",
     "label": "How willing are you to take risks in general?",
     "low": "Not willing at all", "high": "Very willing"},
    {"key": "risk_business",
     "label": "How willing are you to take risks in business decisions?",
     "low": "Not willing at all", "high": "Very willing"},
    {"key": "ambiguity",
     "label": "Some decisions come with known odds, others with odds nobody can "
              "put a number on. How comfortable are you deciding when the odds "
              "are unknown?",
     "low": "Not comfortable at all", "high": "Very comfortable"},
]

# --------------------------------------------------------------------------
# How it works (examples, not part of the study)
# --------------------------------------------------------------------------

WARMUP_INTRO = {
    "title": "How the simulation works",
    "points": [
        ("You run a fictional startup",
         "About 16 decisions in four areas: building the product, finance, "
         "team and go-to-market."),
        ("Your numbers travel with you",
         "Cash, runway, team and customers change with your choices. You see "
         "where you stand at the start and end of each area."),
        ("Two kinds of questions",
         "Most ask you to pick an option. Some ask for two numbers, a best "
         "case and a worst case, so that your answer is a range."),
    ],
    "footer": "The next two screens are short examples to help you get familiar "
              "with the format. They are not part of the study.",
}

PRACTICE_CHOICE = {
    "tag": "Example",
    "question": "Your team meets at a café on Monday morning. What do you order?",
    "options": ["Espresso", "Cappuccino", "Filter coffee", "Tea", "Water"],
}

PRACTICE_RANGE = {
    "tag": "Example",
    "question": "How many cups of coffee does your team drink in a typical week?",
    "intro": "For questions like this, give a low and a high number, so that you "
             "are fairly sure the real value lies between them.",
    "low_label": "Low estimate",
    "low_help": "Only 1 in 10 weeks would be lower than this.",
    "high_label": "High estimate",
    "high_help": "Only 1 in 10 weeks would be higher than this.",
    "unit": "cups",
}

# --------------------------------------------------------------------------
# Your startup
# --------------------------------------------------------------------------

SETUP = {
    "question": "Set up your startup",
    "body": "From here on you are in the simulation.",
    "name_label": "Give your startup a name",
    "name_placeholder": "anything you like",
    "industry_label": "Which industry is it in?",
    "solo_label": "Do you run it alone or with co-founders?",
    "solo_options": ["With co-founders", "Alone"],
}

STARTING_SITUATION = {
    "title": "Your starting situation",
    "body": "This is where you take over. The numbers change with your "
            "decisions, and you see where you stand at the start and end of "
            "each area. Hover over or tap the (i) next to a label to see what "
            "it means.",
    "button": "Start the first area",
}

# --------------------------------------------------------------------------
# The four domain blocks
# --------------------------------------------------------------------------
# "sequence" nodes keep their order because each builds on the one before.
# "floating" nodes are inserted at a random position in the block, which also
# randomises where the attention check sits.

BLOCKS = {
    "team": {
        "title": "Building the product",
        "intro": "You and your co-founders have agreed to build a first version "
                 "of the product, the minimum viable product (MVP). The next "
                 "decisions are about how you get it done.",
        "intro_solo": "You have decided to build a first version of the product, "
                      "the minimum viable product (MVP). The next decisions are "
                      "about how you get it done.",
        "sequence": ["T1", "T3"],
        "floating": ["T2", "T4"],
    },
    "finance": {
        "title": "Finance",
        "intro": "Cash is going out every month. The next decisions are about "
                 "financing the startup.",
        "sequence": ["F1", "F3", "F4"],
        "floating": ["F2"],
    },
    "hiring": {
        "title": "Team",
        "intro": "The work is outgrowing the founding team. The next decisions "
                 "are about who joins and when.",
        "intro_solo": "The work is outgrowing what you can do alone. The next "
                      "decisions are about who joins and when.",
        "sequence": ["H1", "H3", "H4"],
        "floating": ["H2"],
    },
    "gtm": {
        "title": "Go-to-market",
        "intro": "The product is ready enough to sell. The next decisions are "
                 "about how you reach customers.",
        "sequence": ["G1", "G3"],
        "floating": ["G2", "G4"],
    },
}

TRACKS = {
    1: ["team", "finance", "hiring", "gtm"],
    2: ["team", "gtm", "finance", "hiring"],
}

ILLUSTRATIVE = ("The scenario is fictional. Its numbers are illustrative and "
                "set to resemble an early-stage startup.")

# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------
# Money is shown as €12,000. "event" is the line that appears in the summary
# at the end of the area when the option changes a number.
# --------------------------------------------------------------------------

SCREENS = {

    # ------------------------------------------------------- Building the product
    "T1": {
        "kind": "choice",
        "question": "The MVP has 5 core features. How much of the development do "
                    "you do in-house?",
        "body": "Building in-house costs no cash but takes founder time away "
                "from fundraising, hiring and sales. External developers are "
                "paid from your cash.",
        "scenario": ILLUSTRATIVE + " Costs reflect freelance and agency rates "
                    "for a 5-feature MVP. A typical MVP takes about three to "
                    "four months.",
        "sources": ["Netguru, How long does it take to build an MVP? (industry "
                    "guide)"],
        "event": "MVP development",
        "options": [
            {"key": "A", "label": "Everything in-house",
             "label_solo": "Everything myself", "cost": 0,
             "effects": {"morale": -1}},
            {"key": "B", "label": "About three quarters in-house, the rest to "
                                  "freelancers",
             "label_solo": "About three quarters myself, the rest to freelancers",
             "cost": 6_000, "effects": {"cash": -6_000}},
            {"key": "C", "label": "About half to external developers",
             "cost": 12_000, "effects": {"cash": -12_000}},
            {"key": "D", "label": "Almost everything to external developers",
             "cost": 20_000, "effects": {"cash": -20_000, "morale": 1}},
        ],
    },

    "T2": {
        "kind": "contest",
        "question": "A mentor invites you to a pitch contest against 9 other "
                    "startups.",
        "body": "An independent jury ranks all 10 startups on the quality of "
                "their plan. The best one wins a grant of {prize}. Taking part "
                "costs {base_cost} in travel and preparation.",
        "scenario": ILLUSTRATIVE + " One winner is chosen by the jury.",
        "event": "Pitch contest",
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
        "scenario": ILLUSTRATIVE + " Industry guides put a typical MVP at "
                    "about three to four months, with wide variation.",
        "sources": ["Netguru, How long does it take to build an MVP? (industry "
                    "guide)"],
        "unit": "weeks",
        "optimistic_is_high": False,
        "best_label": "Best case",
        "best_help": "Only 1 in 10 similar projects would be ready sooner.",
        "worst_label": "Worst case",
        "worst_help": "Only 1 in 10 similar projects would take longer.",
        "min_value": 1, "max_value": 400, "step": 1,
    },

    "T4": {
        "kind": "choice",
        "question": "How do you run the weekly team meeting?",
        "body": "To show that you are reading carefully, please select "
                "“Standing meeting, 15 minutes” for this question.",
        "options": [
            {"key": "A", "label": "Fixed agenda, 30 minutes", "effects": {}},
            {"key": "B", "label": "Open round without agenda", "effects": {}},
            {"key": "C", "label": "Written updates instead of a meeting",
             "effects": {}},
            {"key": "D", "label": "Standing meeting, 15 minutes", "effects": {}},
        ],
    },

    # ----------------------------------------------------------------- Finance
    "F1": {
        "kind": "choice",
        "question": "You have {runway} months of runway. When do you start "
                    "fundraising?",
        "body": "Starting means preparing the deck and contacting investors. "
                "Closing a round comes later.",
        "scenario": ILLUSTRATIVE + " A seed round usually takes several months "
                    "from first contact to money in the bank.",
        "sources": ["Elad Gil, Fundraising will take you ~3 months (blog)",
                    "DocSend, A brief anatomy of a successful seed raise "
                    "(2020, 175 seed-stage startups)"],
        "event": "Fundraising timing",
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
        "question": "A well-known accelerator has shortlisted you and 9 other "
                    "startups for a single place in its program.",
        "body": "The place comes with {prize} in funding. An independent "
                "selection panel picks the strongest of the 10. Applying, with "
                "a video and two interview rounds, costs {base_cost} in time "
                "and travel.",
        "scenario": ILLUSTRATIVE + " One place, chosen by the panel.",
        "event": "Accelerator application",
        "options": [
            {"key": "A", "label": "Do not apply"},
            {"key": "B", "label": "Apply"},
            {"key": "C", "label": "Apply with an experienced mentor reviewing "
                                  "your application",
             "extra": "mentor review raises the chance of being picked"},
        ],
    },

    "F3": {
        "kind": "interval",
        "chart": "revenue",
        "question": "You are preparing your pitch for a seed round. Monthly "
                    "revenue is now €8,000. What will monthly revenue be in 12 "
                    "months?",
        "scenario": ILLUSTRATIVE + " The revenue path resembles an early-stage "
                    "B2B software company.",
        "sources": ["SaaS Capital, Benchmarking private SaaS company growth "
                    "rates (2025)"],
        "unit": "euros",
        "optimistic_is_high": True,
        "best_label": "Best case",
        "best_help": "Only 1 in 10 comparable startups would end up higher.",
        "worst_label": "Worst case",
        "worst_help": "Only 1 in 10 comparable startups would end up lower.",
        "min_value": 0, "max_value": 10_000_000, "step": 500,
    },

    "F4": {
        "kind": "choice",
        "question": "You need €300,000 to reach the next milestone. Which route "
                    "do you take?",
        "scenario": ILLUSTRATIVE + " At pre-seed, most rounds are raised on "
                    "SAFEs or convertible notes rather than priced rounds.",
        "sources": ["Carta, State of Pre-Seed: 2025 in review",
                    "Y Combinator, Post-money SAFE user guide"],
        "event": "Financing",
        "options": [
            {"key": "A", "label": "Bank loan over 24 months at 9 percent",
             "extra": "about €13,700 per month, no equity given up",
             "effects": {"cash": 300_000, "burn": 13_700}},
            {"key": "B", "label": "SAFE (simple agreement for future equity) with a "
                                  "€6 million valuation cap",
             "extra": "up to 5 percent, final stake set in the next round",
             "effects": {"cash": 300_000}},
            {"key": "C", "label": "Priced round: 5 percent for €300,000",
             "extra": "the investor joins as a board observer, about €15,000 "
                      "in legal costs",
             "effects": {"cash": 285_000}},
        ],
    },

    # --------------------------------------------------------------------- Team
    "H1": {
        "kind": "choice",
        "display": "pills",
        "question": "How many new roles do you open in the next 3 months?",
        "body": "Opening a role starts the search. A role only adds to the team "
                "once someone signs.",
        "scenario": ILLUSTRATIVE + " Filling a technical role takes about ten "
                    "weeks from opening to first hire at a typical tech "
                    "company.",
        "sources": ["Ashby, hiring benchmarks press release (May 2026, "
                    "200,000+ jobs)"],
        "event": "Roles opened",
        "options": [
            {"key": "A", "label": "0", "effects": {"pending_hires": 0}},
            {"key": "B", "label": "1", "effects": {"pending_hires": 1}},
            {"key": "C", "label": "2", "effects": {"pending_hires": 2}},
            {"key": "D", "label": "3",
             "effects": {"pending_hires": 3, "morale": -1}},
            {"key": "E", "label": "4",
             "effects": {"pending_hires": 4, "morale": -1}},
            {"key": "F", "label": "5",
             "effects": {"pending_hires": 5, "morale": -1}},
            {"key": "G", "label": "6 or more",
             "effects": {"pending_hires": 6, "morale": -1}},
        ],
    },

    "H2": {
        "kind": "contest",
        "question": "An experienced Head of Growth is choosing between offers "
                    "from 10 startups, yours among them.",
        "body": "If she joins you, you save 3 months of searching, worth "
                "{prize}. Preparing a standard offer, with an assessment day "
                "and employer branding, costs {base_cost}.",
        "scenario": ILLUSTRATIVE + " She accepts one of the 10 offers.",
        "event": "Offer to Head of Growth",
        "options": [
            {"key": "A", "label": "Make no offer"},
            {"key": "B", "label": "Standard offer"},
            {"key": "C", "label": "Premium offer with more equity",
             "extra": "better terms raise the chance she picks you"},
        ],
    },

    "H3": {
        "kind": "interval",
        "question": "You start searching for a senior backend engineer today. "
                    "How many weeks until a contract is signed?",
        "scenario": ILLUSTRATIVE + " A full-time, permanent senior role, "
                    "searched for without an external recruiter.",
        "sources": ["Ashby, hiring benchmarks press release (May 2026)"],
        "unit": "weeks",
        "optimistic_is_high": False,
        "best_label": "Best case",
        "best_help": "Only 1 in 10 comparable searches would be faster.",
        "worst_label": "Worst case",
        "worst_help": "Only 1 in 10 comparable searches would be slower.",
        "min_value": 1, "max_value": 200, "step": 1,
    },

    "H4": {
        "kind": "choice",
        "question": "You need a Head of Sales. Two finalists remain.",
        "body": "Candidate A scored 82 of 100 on a structured work sample and "
                "has solid references. Candidate B scored 71 of 100 but was the "
                "most convincing person in the interview and gave you a very "
                "strong gut feeling. Either hire adds €7,000 to monthly burn.",
        "event": "Head of Sales",
        "options": [
            {"key": "A", "label": "Hire A",
             "effects": {"burn": 7_000, "team_size": 1}},
            {"key": "B", "label": "Hire B",
             "effects": {"burn": 7_000, "team_size": 1}},
            {"key": "C", "label": "Add a second structured round before "
                                  "deciding",
             "extra": "2 weeks, €2,000",
             "effects": {"cash": -2_000}},
        ],
    },

    # ------------------------------------------------------------ Go-to-market
    "G1": {
        "kind": "choice",
        "question": "You set aside {launch_budget} for the launch. How do you "
                    "split it?",
        "body": "Your <b>first channel</b> is the one you believe in most, "
                "based on talks with early customers. The rest goes into small "
                "tests of two or three other channels to see which ones work.",
        "scenario": ILLUSTRATIVE + " The launch budget is a quarter of your "
                    "current cash.",
        "event": "Launch budget",
        "options": [
            {"key": "A", "label": "100% first channel, no tests",
             "effects": {"spend_launch_budget": True, "customers": 40,
                         "market_confidence": -1}},
            {"key": "B", "label": "70% first channel, 30% tests",
             "effects": {"spend_launch_budget": True, "customers": 50}},
            {"key": "C", "label": "40% first channel, 60% tests",
             "effects": {"spend_launch_budget": True, "customers": 45,
                         "market_confidence": 1}},
            {"key": "D", "label": "20% first channel, 80% tests",
             "effects": {"spend_launch_budget": True, "customers": 30,
                         "market_confidence": 1}},
        ],
    },

    "G2": {
        "kind": "contest",
        "question": "A large potential customer is putting a contract worth "
                    "{prize} out to tender.",
        "body": "Ten startups apply and an independent panel picks the best "
                "proposal. A basic application costs {base_cost}.",
        "scenario": ILLUSTRATIVE + " One contract, awarded by the panel.",
        "event": "Customer tender",
        "options": [
            {"key": "A", "label": "Do not apply"},
            {"key": "B", "label": "Basic application"},
            {"key": "C", "label": "Full application with a pilot demo",
             "extra": "a pilot demo raises the chance of winning"},
        ],
    },

    "G3": {
        "kind": "interval",
        "chart": "customers",
        "question": "A new sales channel brought 40, 65 and 90 new paying "
                    "customers in its first three months. How many new "
                    "customers will it bring in the following six months, in "
                    "total?",
        "scenario": ILLUSTRATIVE + " A paid acquisition channel in its first "
                    "months.",
        "unit": "customers",
        "optimistic_is_high": True,
        "best_label": "Best case",
        "best_help": "Only 1 in 10 comparable channels would bring more.",
        "worst_label": "Worst case",
        "worst_help": "Only 1 in 10 comparable channels would bring fewer.",
        "min_value": 0, "max_value": 100_000, "step": 10,
    },

    "G4": {
        "kind": "multi",
        "question": "A big trade fair is coming up. What do you plan for the two "
                    "days?",
        "body": "Select all that apply. To show that you are reading carefully, "
                "please include “The investor breakfast” in your selection.",
        "options": [
            {"key": "A", "label": "Three customer meetings a day"},
            {"key": "B", "label": "Walk the floor to see competitors"},
            {"key": "C", "label": "The investor breakfast"},
            {"key": "D", "label": "A short talk on the main stage"},
            {"key": "E", "label": "Collect leads at a small booth"},
        ],
    },
}

# Charts shown above the two interval questions that are built on a series.
CHART_REVENUE = [("3 months ago", 6_070, None), ("2 months ago", 6_620, "+9%"),
                 ("Last month", 7_550, "+14%"), ("This month", 8_000, "+6%")]
CHART_CUSTOMERS = [("Month 1", 40, None), ("Month 2", 65, None),
                   ("Month 3", 90, None)]

# --------------------------------------------------------------------------
# Wrap-up
# --------------------------------------------------------------------------

SUSPICION = {
    "title": "One last question",
    "lead": "You have finished the simulation.",
    "question": "What do you think this study was about?",
    "body": "There is no right or wrong answer. A sentence or two in your own "
            "words is enough.",
}

END = {
    "title": "Thank you",
    "body": """
That is everything for today. Thank you for your time, and for taking the decisions as seriously as you did.

**In one week** we will email you a short follow-up of about 5 minutes.
""",
}

THANK_YOU_NOT_FOUNDER = (
    "Thank you for your interest. This study is open to founders and "
    "co-founders only, so the session ends here. Nothing has been stored."
)

DECLINED = "No problem. Nothing has been stored. You can close this page."
