"""Every word a participant sees, plus the effect table that drives the story.

Kept deliberately separate from codebook.json: this file is the story, which
participants experience, and the codebook holds the hidden reference values.

Rules for this file
- Nothing names confidence, calibration or overconfidence.
- No benchmark that could serve as an answer appears anywhere. The "About this
  scenario" popover says the scenario is fictional and names the scientific
  background by author and year only, never the content.
- Text can use {name} (the startup's name), {industry} (a short industry label),
  {runway} and {launch_budget}. app.fill() supplies them.
- American English, "startup", typographic apostrophes.
"""

APP_VERSION = "0.7.0"

# --------------------------------------------------------------------------
# Contact details. Replace the study address once the team mailbox exists.
# --------------------------------------------------------------------------

CONTACT_EMAIL = "[study email]"
WITHDRAWAL_WEEKS = 4

# --------------------------------------------------------------------------
# Starting situation and the economics of the story
# --------------------------------------------------------------------------
# Net burn = monthly costs − monthly revenue. Revenue follows the number of
# customers at a fixed average revenue per customer (90 customers ≈ €8,000).

REVENUE_PER_CUSTOMER = 8_000 / 90
COST_PER_HIRE = 5_000            # monthly cost of each new team member
SHORT_RUNWAY_MONTHS = 6          # below this, the team feels it (morale −1)

START_STATE = {
    "cash": 280_000,
    "costs": 28_000,
    "customers": 90,
    "team_size": 2,              # 1 for solo founders
    "pending_hires": 0,          # roles opened in H1, join at the end of Team
    "pending_cost": 0,           # monthly cost of those who join
    "morale": 3,
    "market_confidence": 3,
    "ownership": 100,            # founders' combined share, in percent
    "fundraise_delay": 0,        # months chosen in F1
}

STATUS_FIELDS = [
    # key, label, help text
    ("cash", "Cash", "Money in the bank right now."),
    ("burn", "Net burn per month", "Monthly costs minus monthly revenue. This "
                                   "is what the startup loses each month."),
    ("runway", "Runway", "How many months the cash lasts. Cash divided by net "
                         "burn per month."),
    ("revenue", "Revenue per month", "Recurring revenue from paying customers."),
    ("customers", "Customers", "Paying customers using the product today."),
    ("team_size", "Team", "People working in the startup, founders included."),
    ("pending_hires", "Open roles", "Positions you have opened. New hires join "
                                    "the team at the end of the Team area."),
    ("ownership", "Founders’ ownership", "Share of the company held by the "
                                         "founders."),
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
    "Food and beverages",
    "Media and entertainment",
    "Other",
]

# Short labels used inside sentences ("an early-stage fintech startup").
INDUSTRY_LABELS = {
    "Software and SaaS": "software",
    "Marketplace or e-commerce": "e-commerce",
    "Fintech or insurtech": "fintech",
    "Health and life sciences": "health",
    "Industrial, hardware or deep tech": "deep tech",
    "Consumer products or services": "consumer",
    "Energy, mobility or climate": "climate",
    "Education": "education",
    "Food and beverages": "food",
    "Media and entertainment": "media",
}

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
        ("A 5-minute follow-up", "By email, a week from now"),
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
    "help": "Current or past, any size and any industry. Joining a company "
            "within its first five years with at least 5% of the equity counts "
            "too.",
    "options": ["Yes", "No"],
}

EMAIL = {
    "question": "Your email address",
    "body": "We use it for one thing only: to send you a short follow-up a week "
            "from now. It is stored separately from your answers and never "
            "shared outside the research team.",
    "label": "Email",
    "placeholder": "name@example.com",
}

# --------------------------------------------------------------------------
# About you (not part of the simulation)
# --------------------------------------------------------------------------

ABOUT_NOTE = "This part is about you, not the simulation."
OTHER_LABEL = "Please specify"

PROFILE = {
    "question": "About you and your company",
    "body": "A few questions for the analysis. If you no longer run a company, "
            "answer for the most recent one. Your answers are never published "
            "individually.",
}

PROFILE_FIELDS = [
    {"key": "age", "label": "Your age", "kind": "number", "min": 18, "max": 99,
     "col": 0},
    {"key": "gender", "label": "Gender", "kind": "select", "col": 1,
     "options": ["Female", "Male", "Non-binary", "Prefer not to say"]},
    {"key": "education", "label": "Highest degree completed", "kind": "select",
     "col": 0,
     "options": ["No formal degree", "High school diploma", "Apprenticeship",
                 "Bachelor’s degree", "Master’s degree or Diploma", "Doctorate",
                 "Prefer not to say"]},
    {"key": "country", "label": "Country your company is based in",
     "kind": "select", "options": COUNTRIES, "col": 1},
    {"key": "industry_real", "label": "Industry of your company", "kind": "select",
     "options": INDUSTRIES},
    {"key": "previous_startups", "label": "Companies you founded before this one",
     "kind": "pills", "options": ["0", "1", "2", "3 or more"]},
    {"key": "years_founder",
     "label": "Years of experience as a founder (0 if this is your first year)",
     "kind": "number", "min": 0, "max": 60, "col": 0},
    {"key": "employees",
     "label": "People employed in your company, not counting the founders",
     "kind": "number", "min": 0, "max": 100_000, "col": 1},
    {"key": "stage", "label": "Stage of your company", "kind": "select",
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
    "question": "How often have you done this before?",
    "body": "Count everything across your career, not only your current company.",
}
EXPERIENCE_FIELDS = [
    {"key": "exp_financing",
     "label": "Times you have raised external financing (investors, loans or grants)",
     "options": ["0", "1", "2", "3", "4", "5 or more"]},
    {"key": "exp_teams", "label": "Founding teams you have been part of",
     "options": ["0", "1", "2", "3", "4 or more"]},
    {"key": "exp_hires", "label": "People you have hired",
     "options": ["0", "1 to 2", "3 to 5", "6 to 10", "More than 10"]},
    {"key": "exp_launches", "label": "Product launches you have run",
     "options": ["0", "1", "2", "3", "4", "5 or more"]},
]

# Risk items 1 and 2: SOEP general and occupational risk questions, validated
# by Dohmen et al. (2011, Journal of the European Economic Association).
# Item 3: ambiguity attitude, own short wording (see codebook).
RISK = {
    "question": "How you decide",
    "body": "Three questions about your general attitude. Pick a point on each "
            "scale.",
}
RISK_ITEMS = [
    {"key": "risk_general",
     "label": "How willing are you to take risks, in general?",
     "low": "Not at all willing to take risks",
     "high": "Very willing to take risks"},
    {"key": "risk_occupation",
     "label": "How willing are you to take risks in your occupation?",
     "low": "Not at all willing to take risks",
     "high": "Very willing to take risks"},
    {"key": "ambiguity",
     "label": "How comfortable are you making decisions when nobody can say how "
              "likely each outcome is?",
     "low": "Not at all comfortable", "high": "Very comfortable"},
]

# --------------------------------------------------------------------------
# How it works (examples, not part of the study)
# --------------------------------------------------------------------------

WARMUP_INTRO = {
    "title": "How the simulation works",
    "points": [
        ("You run a fictional startup",
         "About 20 decisions in four areas: building the product, finance, team "
         "and go-to-market."),
        ("Your numbers travel with you",
         "Cash, runway, team and customers change with your choices. You see "
         "your current status at the start and end of each area."),
        ("Two kinds of questions",
         "Most ask you to pick an option. Some ask for a low and a high "
         "estimate, so that your answer is a range."),
    ],
    "footer": "The next two screens are short examples to help you get familiar "
              "with the format. They are not part of the study.",
}

PRACTICE_CHOICE = {
    "tag": "Example",
    "question": "You start Monday morning at a café. What do you order?",
    "options": ["Espresso", "Cappuccino", "Filter coffee", "Tea", "Water"],
}

PRACTICE_RANGE = {
    "tag": "Example",
    "question": "How many cups of coffee do you drink in a typical week?",
    "low_help": "Only 1 in 10 weeks would be lower than this.",
    "high_help": "Only 1 in 10 weeks would be higher than this.",
    "unit": "cups",
}

RANGE_INSTRUCTION = ("Give a low and a high estimate, so that you are 80% sure "
                     "the real value lies between them.")

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
    "body": "This is where you take over {name}. The numbers change with your "
            "decisions, and you see your current status at the start and end "
            "of each area. Hover over or tap the (i) next to a label to see "
            "what it means.",
    "button": "Start the first area",
}

# --------------------------------------------------------------------------
# The four domain blocks
# --------------------------------------------------------------------------
# "sequence" nodes keep their order because each builds on the one before.
# "units" are groups that stay together (the rank question comes right before
# its contest) and are inserted at a random position. The two attention checks
# are placed by flow.py into the second and third area of the track.

BLOCKS = {
    "team": {
        "title": "Building the product",
        "intro": "You and your co-founders have agreed to build a first version "
                 "of {name}, the minimum viable product (MVP). The next "
                 "decisions are about how you get it done.",
        "intro_solo": "You have decided to build a first version of {name}, the "
                      "minimum viable product (MVP). The next decisions are "
                      "about how you get it done.",
        "sequence": ["T1", "T3"],
        "units": [["T5", "T2"]],
    },
    "finance": {
        "title": "Finance",
        "intro": "{name} loses money every month until revenue covers the costs. "
                 "The next decisions are about financing.",
        "sequence": ["F1", "F3", "F4"],
        "units": [["F5", "F2"]],
    },
    "hiring": {
        "title": "Team",
        "intro": "The work is outgrowing what your team can do. The next "
                 "decisions are about who joins and when.",
        "intro_solo": "The work is outgrowing what you can do alone. The next "
                      "decisions are about who joins and when.",
        "sequence": ["H1", "H3", "H4"],
        "units": [["H5", "H2"]],
    },
    "gtm": {
        "title": "Go-to-market",
        "intro": "{name} is ready enough to sell. The next decisions are about "
                 "how you reach customers.",
        "sequence": ["G1", "G3"],
        "units": [["G5", "G2"]],
    },
}

TRACKS = {
    1: ["team", "finance", "hiring", "gtm"],
    2: ["team", "gtm", "finance", "hiring"],
}

ATTENTION_CHECKS = ["AC1", "AC2"]      # into areas 2 and 3 of every track

FICTIONAL = "The scenario is fictional."
CONTEST_NOTE = "Results are announced after the study."

# Background shown in the popover, author and year only.
BG_CONTEST = ["Camerer & Lovallo (1999)", "Moore & Cain (2007)"]
BG_RANK = ["Moore & Healy (2008)", "Benoît, Dubra & Moore (2015)"]

# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------

SCREENS = {

    # ------------------------------------------------------- Building the product
    "T1": {
        "kind": "choice",
        "question": "The MVP of {name} has 5 core features. How much of the "
                    "development do you do in-house?",
        "question_solo": "The MVP of {name} has 5 core features. How much of the "
                         "development do you do yourself?",
        "body": "In-house work costs no cash but takes founder time away from "
                "fundraising, hiring and sales. External developers are paid "
                "from your cash.",
        "background": ["Kahneman & Lovallo (1993)", "Buehler, Griffin & Ross (1994)"],
        "event": "MVP development",
        "options": [
            {"key": "A", "label": "Everything in-house",
             "label_solo": "Everything myself",
             "extra": "no cash cost · about 12 weeks of founder time",
             "effects": {"morale": -1}},
            {"key": "B", "label": "About three quarters in-house, the rest to "
                                  "freelancers",
             "label_solo": "About three quarters myself, the rest to freelancers",
             "extra": "€6,000 · about 8 weeks of founder time",
             "effects": {"cash": -6_000}},
            {"key": "C", "label": "About half to external developers",
             "extra": "€12,000 · about 5 weeks of founder time",
             "effects": {"cash": -12_000}},
            {"key": "D", "label": "Almost everything to external developers",
             "extra": "€20,000 · about 2 weeks of founder time",
             "effects": {"cash": -20_000}},
        ],
    },

    "T5": {
        "kind": "rank",
        "contest": "T2",
        "question": "A mentor invites {name} to a pitch contest. An independent "
                    "jury will rank the plans of all 10 invited startups.",
        "body": "Before you decide whether to take part: if the jury ranked all "
                "10 plans, where would {name} land?",
        "background": BG_RANK,
    },

    "T2": {
        "kind": "contest",
        "question": "Do you take part in the pitch contest?",
        "body": "The jury ranks the plans of all 10 startups. The best one wins "
                "a grant of {prize}. Taking part costs {base_cost} in travel and "
                "preparation. An average startup has a 1 in 10 chance of "
                "winning.",
        "background": BG_CONTEST,
        "event": "Pitch contest",
        "options": [
            {"key": "A", "label": "Do not take part"},
            {"key": "B", "label": "Take part"},
            {"key": "C", "label": "Take part with pitch coaching",
             "extra": "raises an average startup’s chance to 1 in 8"},
        ],
    },

    "T3": {
        "kind": "interval",
        "question": "Assume the equivalent of 2 full-time developers work on the "
                    "5 core features of the MVP. How many weeks until it is "
                    "ready?",
        "background": ["Jørgensen (2004)", "Flyvbjerg & Budzier (2011)"],
        "unit": "weeks",
        "optimistic_is_high": False,
        "low_help": "Only 1 in 10 similar projects would be ready sooner.",
        "high_help": "Only 1 in 10 similar projects would take longer.",
        "min_value": 1, "max_value": 400, "step": 1,
    },

    # ----------------------------------------------------------------- Finance
    "F1": {
        "kind": "choice",
        "question": "{name} has {runway} months of runway. When do you start "
                    "fundraising?",
        "body": "Starting means preparing the deck and contacting investors. "
                "Until then, {name} keeps paying its running costs from the "
                "cash it has.",
        "background": ["DocSend (2020)", "Gil (2018)"],
        "event": "Fundraising starts",
        "options": [
            {"key": "A", "label": "Right away", "effects": {"fundraise_delay": 0}},
            {"key": "B", "label": "In 3 months", "effects": {"fundraise_delay": 3}},
            {"key": "C", "label": "In 6 months", "effects": {"fundraise_delay": 6}},
            {"key": "D", "label": "In 9 months",
             "effects": {"fundraise_delay": 9, "market_confidence": -1}},
        ],
    },

    "F5": {
        "kind": "rank",
        "contest": "F2",
        "question": "A well-known accelerator has shortlisted {name} and 9 other "
                    "startups for a single place in its program.",
        "body": "Before you decide whether to apply: if the selection panel "
                "ranked all 10 startups, where would {name} land?",
        "background": BG_RANK,
    },

    "F2": {
        "kind": "contest",
        "question": "Do you apply for the accelerator place?",
        "body": "The place comes with {prize} as a grant, no equity taken. An "
                "independent panel picks the strongest of the 10. Applying, with "
                "a video and two interview rounds, costs {base_cost} in time and "
                "travel. An average startup has a 1 in 10 chance of being picked.",
        "background": BG_CONTEST,
        "event": "Accelerator application",
        "options": [
            {"key": "A", "label": "Do not apply"},
            {"key": "B", "label": "Apply"},
            {"key": "C", "label": "Apply with an experienced mentor reviewing "
                                  "your application",
             "extra": "raises an average startup’s chance to 1 in 8"},
        ],
    },

    "F3": {
        "kind": "interval",
        "chart": "revenue",
        "question": "{name} is preparing its pitch for a seed round. Monthly "
                    "revenue is {revenue_now} today. What will monthly revenue be "
                    "in 12 months?",
        "scenario_extra": "The revenue path is that of an early-stage {industry} "
                          "startup.",
        "background": ["SaaS Capital (2025)"],
        "unit": "euros",
        "optimistic_is_high": True,
        "low_help": "Only 1 in 10 comparable startups would end up lower.",
        "high_help": "Only 1 in 10 comparable startups would end up higher.",
        "min_value": 0, "max_value": 10_000_000, "step": 500,
    },

    "F4": {
        "kind": "choice",
        "question": "{name} needs €300,000 to reach the next milestone. Which "
                    "route do you take?",
        "background": ["Carta (2026)"],
        "event": "Financing",
        "options": [
            {"key": "A", "label": "Bank loan over 24 months at 9 percent",
             "extra": "about €13,700 per month in repayments, no equity given up",
             "effects": {"raise": 300_000, "costs": 13_700}},
            {"key": "B", "label": "SAFE (simple agreement for future equity) with "
                                  "a €6 million valuation cap",
             "extra": "up to 5% of the company, final stake set in the next round",
             "effects": {"raise": 300_000, "ownership": -5}},
            {"key": "C", "label": "Priced round: 5% of the company for €300,000",
             "extra": "the investor joins as a board observer, about €15,000 in "
                      "legal costs",
             "effects": {"raise": 285_000, "ownership": -5,
                         "market_confidence": 1}},
        ],
    },

    # --------------------------------------------------------------------- Team
    "H1": {
        "kind": "choice",
        "display": "pills",
        "question": "How many new roles do you open in the next 3 months?",
        "body": "Opening a role starts the search. New hires join the team at the "
                "end of this area. Each new hire adds about €5,000 to the monthly "
                "costs.",
        "background": ["Ashby (2026)"],
        "event": "Roles opened",
        "options": [
            {"key": "A", "label": "0", "effects": {"pending_hires": 0}},
            {"key": "B", "label": "1", "effects": {"pending_hires": 1}},
            {"key": "C", "label": "2", "effects": {"pending_hires": 2}},
            {"key": "D", "label": "3", "effects": {"pending_hires": 3}},
            {"key": "E", "label": "4", "effects": {"pending_hires": 4}},
            {"key": "F", "label": "5", "effects": {"pending_hires": 5}},
            {"key": "G", "label": "6 or more", "effects": {"pending_hires": 6}},
        ],
    },

    "H5": {
        "kind": "rank",
        "contest": "H2",
        "question": "An experienced Head of Growth is choosing between offers from "
                    "10 startups, {name} among them.",
        "body": "Before you decide whether to make an offer: if she ranked all 10 "
                "startups by how attractive they are to her, where would {name} "
                "land?",
        "background": BG_RANK,
    },

    "H2": {
        "kind": "contest",
        "question": "Do you make the Head of Growth an offer?",
        "body": "If she joins you, you save 3 months of searching, worth {prize}. "
                "Preparing a standard offer, with an assessment day and employer "
                "branding, costs {base_cost}. An average startup has a 1 in 10 "
                "chance of being her choice.",
        "background": BG_CONTEST,
        "event": "Offer to Head of Growth",
        "options": [
            {"key": "A", "label": "Make no offer"},
            {"key": "B", "label": "Standard offer"},
            {"key": "C", "label": "Premium offer with a higher salary and a "
                                  "signing bonus",
             "extra": "raises an average startup’s chance to 1 in 8"},
        ],
    },

    "H3": {
        "kind": "interval",
        "question": "You start searching for a senior backend engineer today. How "
                    "many weeks until a contract is signed?",
        "scenario_extra": "A full-time, permanent senior role, searched for "
                          "without an external recruiter.",
        "background": ["Ashby (2026)", "Davis, Faberman & Haltiwanger (2013)"],
        "unit": "weeks",
        "optimistic_is_high": False,
        "low_help": "Only 1 in 10 comparable searches would be faster.",
        "high_help": "Only 1 in 10 comparable searches would be slower.",
        "min_value": 1, "max_value": 200, "step": 1,
    },

    "H4": {
        "kind": "hire",
        "question": "{name} needs a Head of Sales. Two finalists remain.",
        "candidates": {
            "A": "scored 82 of 100 on a structured work sample and has solid "
                 "references",
            "B": "scored 71 of 100 on the work sample but was the most convincing "
                 "person in the interview and gave you a very strong gut feeling",
        },
        "after": "Either hire adds €7,000 to the monthly costs and joins at the end "
                 "of this area.",
        "background": ["Dawes, Faust & Meehl (1989)"],
        "event": "Head of Sales",
        "options": [
            {"key": "A", "effects": {"pending_hires_extra": 1,
                                     "pending_cost_extra": 7_000}},
            {"key": "B", "effects": {"pending_hires_extra": 1,
                                     "pending_cost_extra": 7_000}},
            {"key": "C", "label": "Add a second structured round before deciding",
             "extra": "2 weeks, €2,000", "effects": {"cash": -2_000}},
        ],
    },

    # ------------------------------------------------------------ Go-to-market
    "G1": {
        "kind": "choice",
        "question": "You set aside {launch_budget} for the launch of {name}. How "
                    "do you split it?",
        "body": "Your <b>first channel</b> is the one you believe in most, based on "
                "talks with early customers. The rest goes into small tests of two "
                "or three other channels to see which ones work.",
        "scenario_extra": "The launch budget is a quarter of the cash at the start "
                          "of this area.",
        "background": ["Kohavi & Thomke (2017)"],
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

    "G5": {
        "kind": "rank",
        "contest": "G2",
        "question": "A large potential customer is putting a contract out to "
                    "tender. Ten startups, {name} among them, can apply.",
        "body": "Before you decide whether to apply: if the panel ranked the "
                "proposals of all 10 startups, where would {name} land?",
        "background": BG_RANK,
    },

    "G2": {
        "kind": "contest",
        "question": "Do you apply for the {prize} contract?",
        "body": "An independent panel picks the best of the 10 proposals. A basic "
                "application costs {base_cost}. An average startup has a 1 in 10 "
                "chance of winning.",
        "background": BG_CONTEST,
        "event": "Customer tender",
        "options": [
            {"key": "A", "label": "Do not apply"},
            {"key": "B", "label": "Basic application"},
            {"key": "C", "label": "Full application with a pilot demo",
             "extra": "raises an average startup’s chance to 1 in 8"},
        ],
    },

    "G3": {
        "kind": "interval",
        "chart": "customers",
        "question": "A new sales channel brought {name} 40, 65 and 90 new paying "
                    "customers in its first three months. How many new customers "
                    "will it bring in the following six months, in total?",
        "scenario_extra": "A paid acquisition channel in its first months.",
        "background": ["ChartMogul (2023)"],
        "unit": "customers",
        "optimistic_is_high": True,
        "low_help": "Only 1 in 10 comparable channels would bring fewer.",
        "high_help": "Only 1 in 10 comparable channels would bring more.",
        "min_value": 0, "max_value": 100_000, "step": 10,
    },

    # -------------------------------------------------------- Attention checks
    "AC1": {
        "kind": "choice",
        "question": "How do you plan your working week?",
        "body": "To show that you are reading carefully, please select “A daily "
                "to-do list, no fixed blocks” for this question.",
        "options": [
            {"key": "A", "label": "Fixed time blocks for product, sales and admin",
             "effects": {}},
            {"key": "B", "label": "A daily to-do list, no fixed blocks",
             "effects": {}},
            {"key": "C", "label": "A weekly review with priorities on Monday",
             "effects": {}},
            {"key": "D", "label": "Day by day, as things come up", "effects": {}},
        ],
    },

    "AC2": {
        "kind": "multi",
        "question": "A big trade fair is coming up. What do you plan for the two "
                    "days?",
        "body": "To show that you are reading carefully, please select only "
                "“Collect leads at a small booth” and nothing else.",
        "options": [
            {"key": "A", "label": "Three customer meetings a day"},
            {"key": "B", "label": "Walk the floor to see competitors"},
            {"key": "C", "label": "The investor breakfast"},
            {"key": "D", "label": "A short talk on the main stage"},
            {"key": "E", "label": "Collect leads at a small booth"},
        ],
    },
}

RANK_SCALE = [str(i) for i in range(1, 11)]
RANK_ENDS = ("1 = best of the 10", "10 = last of the 10")

# Charts above the two range questions that build on a series. The revenue
# series is scaled to the revenue at the start of the Finance area, so the chart,
# the question and the status strip always agree (the reference scales with it).
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
    "body": "That is everything for today. Thank you for your time, and for "
            "taking the decisions as seriously as you did.\n\n"
            "**A week from now** we will email you a short follow-up of about 5 "
            "minutes. Once the study is complete, we will also let you know how "
            "the contests turned out.",
}

THANK_YOU_NOT_FOUNDER = (
    "Thank you for your interest. This study is open to founders and "
    "co-founders only, so the session ends here. Nothing has been stored."
)

DECLINED = "No problem. Nothing has been stored. You can close this page."
