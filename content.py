"""Every word a participant sees, plus the effect table that drives the story.

Kept deliberately separate from codebook.json: this file is the story, which
participants experience, and the codebook holds the hidden reference values.
Nothing here names confidence, calibration or overconfidence before the debrief.
"""

APP_VERSION = "0.3.0"

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
    "pending_hires": 0,      # planned in H1, added to team size at end of block
}

STATE_LABELS = {
    "cash": "Cash",
    "burn": "Burn per month",
    "runway": "Runway",
    "team_size": "Team size",
    "morale": "Team morale",
    "market_confidence": "Market confidence",
    "customers": "Customers",
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

# --------------------------------------------------------------------------
# Start of the session (Figure 2, screens 0.1 to 1.2)
# --------------------------------------------------------------------------

CONSENT = {
    "title": "Decisions in founding",
    "body": """
You are invited to take part in a study on how founders make decisions. The session
takes about 20 minutes and is followed by a short questionnaire by mail one week later.

You will run a fictional start-up and make the decisions its founders face. There are
no right or wrong answers, and nothing you enter is checked against your real company.

**Taking part is voluntary.** You can stop at any point. Your answers are stored under a
pseudonym code that you will be shown on the next screens, and you can use that code to
have your data deleted at any time.

**The full purpose of the study will be explained to you at the end of the session**,
before you leave, together with your own results.

Contact: [name, mail address of the research team].
""",
    "agree": "I agree and would like to start",
    "decline": "I do not agree",
}

FILTER = {
    "question": "Are you a founder or co-founder of a start-up?",
    "help": "We count as a founder anyone who founded a venture, inherited or bought one "
            "and runs it, or joined within five years of its founding with at least five "
            "percent of the equity.",
    "options": ["Yes", "No"],
}

SETUP = {
    "name_label": "Give your start-up a name",
    "name_placeholder": "anything you like",
    "industry_label": "Which industry is it in?",
    "solo_label": "Do you run it alone or with co-founders?",
    "solo_options": ["With co-founders", "Alone"],
}

PRACTICE_NAME = {
    "question": "Before we start, two short warm-up screens. They are not part of the study.",
    "product_label": "Choose a name for your first product",
    "colour_label": "And a colour for the logo",
    "colours": ["Blue", "Green", "Orange", "Purple", "Black"],
}

PRACTICE_RANGE = {
    "intro": "One more warm-up. Some questions ask for two numbers rather than one.",
    "low": {
        "question": "How many cups of coffee does your team drink in a week?",
        "prompt": "Give a **low** value: only 1 in 10 weeks would be below it.",
    },
    "high": {
        "question": "How many cups of coffee does your team drink in a week?",
        "prompt": "Now give a **high** value: only 1 in 10 weeks would be above it.",
    },
}

# --------------------------------------------------------------------------
# The four domain blocks
# --------------------------------------------------------------------------

BLOCKS = {
    "team": {
        "number": 2,
        "title": "Your team",
        "intro": "You and your co-founders have decided to build the first version of the "
                 "product. The next decisions are about how you get it done.",
        "intro_solo": "You have decided to build the first version of the product. "
                      "The next decisions are about how you get it done.",
        "nodes": ["T1", "T2", "T3"],
        "last": "T4",
    },
    "finance": {
        "number": 3,
        "title": "Money",
        "intro": "The product is taking shape and the bank balance is not standing still. "
                 "The next decisions are about financing.",
        "nodes": ["F1", "F2", "F3"],
        "last": "F4",
    },
    "hiring": {
        "number": 4,
        "title": "People",
        "intro": "The work is outgrowing the founding team. The next decisions are about "
                 "who joins and when.",
        "nodes": ["H1", "H2", "H3"],
        "last": "H4",
    },
    "gtm": {
        "number": 5,
        "title": "Going to market",
        "intro": "The product is ready enough to sell. The next decisions are about how "
                 "you reach customers.",
        "nodes": ["G1", "G2", "G3"],
        "last": "G4",
    },
}

TRACKS = {
    1: ["team", "finance", "hiring", "gtm"],
    2: ["team", "gtm", "finance", "hiring"],
}

# --------------------------------------------------------------------------
# Screens. "effects" are applied to the state when an option is chosen and are
# the only thing the story reacts to. They never depend on the reference values.
# --------------------------------------------------------------------------

SCREENS = {

    # ---------------------------------------------------------------- Team
    "T1": {
        "kind": "choice",
        "question": "The MVP needs product development. How much of it do you build yourselves?",
        "question_solo": "The MVP needs product development. How much of it do you build yourself?",
        "options": [
            {"key": "A", "label": "Everything ourselves",
             "label_solo": "Everything myself",
             "effects": {"cash": 0, "morale": -1}},
            {"key": "B", "label": "The core ourselves, the rest to freelancers",
             "label_solo": "The core myself, the rest to freelancers",
             "effects": {"cash": -6_000, "morale": 0}},
            {"key": "C", "label": "About half to external developers",
             "effects": {"cash": -12_000, "morale": 0}},
            {"key": "D", "label": "Almost everything to external developers",
             "effects": {"cash": -20_000, "morale": 1}},
        ],
    },

    "T2": {
        "kind": "contest",
        "question": "A mentor invites your team to a pitch contest against 9 other teams.",
        "body": "An independent jury ranks all 10 teams on the quality of their plan. "
                "The best team wins a grant of {prize}. Taking part costs {base_cost} "
                "in travel and preparation.",
        "options": [
            {"key": "A", "label": "Do not take part"},
            {"key": "B", "label": "Take part"},
            {"key": "C", "label": "Take part with coaching",
             "extra": "raises your chance from 1 in 10 to 1 in 8"},
        ],
    },

    "T3": {
        "kind": "interval",
        "question": "Your plan has 5 core features and 2 developers on it. "
                    "How many weeks until the MVP is ready?",
        "unit": "weeks",
        "optimistic_is_high": False,
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 similar projects would finish sooner.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 similar projects would take longer.",
        "min_value": 1, "max_value": 400,
    },

    "T4": {
        "kind": "choice",
        "question": "How do you run the weekly team meeting?",
        "options": [
            {"key": "A", "label": "Fixed agenda, 30 minutes", "effects": {}},
            {"key": "B", "label": "Open round without agenda", "effects": {}},
            {"key": "C", "label": "Please select this option to show you are reading carefully",
             "effects": {}},
            {"key": "D", "label": "Standing meeting, 15 minutes", "effects": {}},
        ],
    },

    # ------------------------------------------------------------- Finance
    "F1": {
        "kind": "choice",
        "question": "You have {runway} months of runway. When do you start fundraising?",
        "options": [
            {"key": "A", "label": "Right away", "effects": {}},
            {"key": "B", "label": "In 3 months", "effects": {}},
            {"key": "C", "label": "In 6 months", "effects": {}},
            {"key": "D", "label": "In 9 months", "effects": {"market_confidence": -1}},
        ],
    },

    "F2": {
        "kind": "contest",
        "question": "A founders' network invites 10 start-ups to a pitch contest.",
        "body": "An independent jury ranks all 10 on the quality of their plan. The best "
                "start-up wins {prize}. Taking part costs {base_cost} in travel, deck and time.",
        "options": [
            {"key": "A", "label": "Do not take part"},
            {"key": "B", "label": "Take part"},
            {"key": "C", "label": "Take part with pitch coaching",
             "extra": "raises your chance from 1 in 10 to 1 in 8"},
        ],
    },

    "F3": {
        "kind": "interval",
        "question": "You are preparing the seed story. Monthly revenue is now 8,000 euros, "
                    "after growth of 9%, 14% and 6% in the last three months. "
                    "What will monthly revenue be in 12 months?",
        "unit": "euros",
        "optimistic_is_high": True,
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 comparable start-ups would end up higher.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 comparable start-ups would end up lower.",
        "min_value": 0, "max_value": 10_000_000,
    },

    "F4": {
        "kind": "choice",
        "question": "You need 300,000 euros to reach the next milestone. Which route do you take?",
        "options": [
            {"key": "A", "label": "Bank loan over 24 months at 9 percent",
             "extra": "about 13,700 euros per month",
             "effects": {"cash": 300_000, "burn": 13_700}},
            {"key": "B", "label": "Convertible note with a 3 million euro cap",
             "effects": {"cash": 300_000}},
            {"key": "C", "label": "Equity round, 20 percent of the company for 300,000 euros",
             "effects": {"cash": 300_000}},
        ],
    },

    # -------------------------------------------------------------- Hiring
    "H1": {
        "kind": "choice",
        "question": "How many roles do you plan to fill in the next 3 months?",
        "options": [
            {"key": "A", "label": "1", "effects": {"burn": 5_000, "pending_hires": 1}},
            {"key": "B", "label": "2", "effects": {"burn": 10_000, "pending_hires": 2}},
            {"key": "C", "label": "4", "effects": {"burn": 20_000, "pending_hires": 4, "morale": -1}},
            {"key": "D", "label": "6", "effects": {"burn": 30_000, "pending_hires": 6, "morale": -1}},
        ],
    },

    "H2": {
        "kind": "contest",
        "question": "A senior developer is choosing between 10 offers, yours among them.",
        "body": "If you win her, you save 3 months of searching, worth {prize}. "
                "A standard offer with an assessment and employer branding costs {base_cost}.",
        "options": [
            {"key": "A", "label": "Make no offer"},
            {"key": "B", "label": "Standard offer"},
            {"key": "C", "label": "Premium offer with more equity",
             "extra": "raises your chance from 1 in 10 to 1 in 8"},
        ],
    },

    "H3": {
        "kind": "interval",
        "question": "How many weeks pass from the start of the search to a signed contract "
                    "for this role?",
        "unit": "weeks",
        "optimistic_is_high": False,
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 comparable searches would be faster.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 comparable searches would be slower.",
        "min_value": 1, "max_value": 200,
    },

    "H4": {
        "kind": "choice",
        "question": "You need a head of sales. Two finalists remain.",
        "body": "Candidate A scored 82 of 100 on a structured work sample and has solid "
                "references. Candidate B scored 71 of 100 but was the most convincing "
                "person in the interview and gave you a very strong gut feeling.",
        "options": [
            {"key": "A", "label": "Hire A", "effects": {"burn": 7_000, "team_size": 1}},
            {"key": "B", "label": "Hire B", "effects": {"burn": 7_000, "team_size": 1}},
            {"key": "C", "label": "Add a second structured round before deciding",
             "extra": "2 weeks, 2,000 euros",
             "effects": {"cash": -2_000}},
        ],
    },

    # --------------------------------------------------------- Go-to-market
    "G1": {
        "kind": "choice",
        "question": "You set aside {launch_budget} for the launch. How do you split it "
                    "between your first channel and tests of other channels?",
        "options": [
            {"key": "A", "label": "100 percent first channel, 0 percent tests",
             "effects": {"spend_launch_budget": True, "customers": 50}},
            {"key": "B", "label": "70 percent first channel, 30 percent tests",
             "effects": {"spend_launch_budget": True, "customers": 50}},
            {"key": "C", "label": "40 percent first channel, 60 percent tests",
             "effects": {"spend_launch_budget": True, "customers": 50}},
            {"key": "D", "label": "20 percent first channel, 80 percent tests",
             "effects": {"spend_launch_budget": True, "customers": 50}},
        ],
    },

    "G2": {
        "kind": "contest",
        "question": "A lead customer is tendering a contract worth {prize}.",
        "body": "10 start-ups apply and an independent panel picks the best proposal. "
                "A basic application costs {base_cost}.",
        "options": [
            {"key": "A", "label": "Do not apply"},
            {"key": "B", "label": "Basic application"},
            {"key": "C", "label": "Full application with a pilot demo",
             "extra": "raises your chance from 1 in 10 to 1 in 8"},
        ],
    },

    "G3": {
        "kind": "interval",
        "question": "A pilot of a new sales channel brought 40, 65 and 90 new paying "
                    "customers in its first three months. How many new customers will it "
                    "bring in the following six months in total?",
        "unit": "customers",
        "optimistic_is_high": True,
        "optimistic_prompt": "Give an **optimistic** value: only 1 in 10 comparable channels would do better.",
        "pessimistic_prompt": "Give a **pessimistic** value: only 1 in 10 comparable channels would do worse.",
        "min_value": 0, "max_value": 100_000,
    },

    "G4": {
        "kind": "choice",
        "question": "Which look do you choose for your website?",
        "options": [
            {"key": "A", "label": "Blue with a calm claim", "effects": {}},
            {"key": "B", "label": "Orange with a bold claim", "effects": {}},
            {"key": "C", "label": "Neutral grey. Please select this option to show you are "
                                  "reading carefully", "effects": {}},
            {"key": "D", "label": "Green with a friendly claim", "effects": {}},
        ],
    },
}

# --------------------------------------------------------------------------
# End of the session (Figure 2, screens 7.1 to 8.3)
# --------------------------------------------------------------------------

SUSPICION = {
    "question": "Before we finish: what do you think this study was about?",
    "prompt": "Please write down whatever comes to mind. There is no wrong answer.",
}

PROFILE_FIELDS = [
    {"key": "age", "label": "Your age", "kind": "number", "min": 16, "max": 99},
    {"key": "gender", "label": "Gender", "kind": "select",
     "options": ["Female", "Male", "Other", "Prefer not to say"]},
    {"key": "education", "label": "Highest degree", "kind": "select",
     "options": ["No degree yet", "Vocational training", "Bachelor", "Master or Diploma",
                 "Doctorate", "Prefer not to say"]},
    {"key": "previous_startups", "label": "Start-ups founded before this one", "kind": "select",
     "options": ["0", "1", "2 or more"]},
    {"key": "years_founder", "label": "Years of experience as a founder", "kind": "number",
     "min": 0, "max": 60},
    {"key": "stage", "label": "Stage of your start-up", "kind": "select",
     "options": ["Pre-seed", "Seed", "Series A or later",
                 "Profitable without external funding"]},
    {"key": "team_size_real", "label": "People in your start-up today", "kind": "number",
     "min": 1, "max": 10_000},
    {"key": "funding", "label": "Main source of financing", "kind": "select",
     "options": ["Bootstrapped", "Angel", "Venture capital", "Grants or public funding",
                 "Other"]},
    {"key": "country", "label": "Country your start-up is based in", "kind": "text"},
]

EXPERIENCE_FIELDS = [
    {"key": "exp_funding", "label": "Funding rounds you have been through"},
    {"key": "exp_cofounder", "label": "Co-founder agreements you have negotiated"},
    {"key": "exp_hires", "label": "People you have hired"},
    {"key": "exp_launches", "label": "Product launches you have run"},
]
EXPERIENCE_OPTIONS = ["0", "1", "2", "3 or more"]

# Requirement R7: risk and ambiguity attitude recorded separately from the scores.
# Missing from the walkthrough of 5 October; added here so R7 can be evaluated.
RISK_ITEMS = [
    {"key": "risk_general",
     "label": "How willing are you to take risks in general?",
     "low": "not at all willing", "high": "very willing"},
    {"key": "risk_business",
     "label": "And how willing are you to take risks in business decisions?",
     "low": "not at all willing", "high": "very willing"},
    {"key": "ambiguity",
     "label": "Some decisions come with known odds, others with odds nobody can put a "
              "number on. How comfortable are you deciding when the odds are unknown?",
     "low": "not at all comfortable", "high": "very comfortable"},
]

DEBRIEF_PURPOSE = {
    "title": "What this study was really about",
    "body": """
Thank you for playing it through. Here is the part we could not tell you at the start.

The study measures **overconfidence in founder decisions**. Research distinguishes three
forms of it, and the session measured each one once in each of the four areas you went
through:

- **Overestimation** — expecting more performance or speed than turns out to be realistic.
  Measured by the planning and budget decisions, such as how much of the MVP you build
  yourselves.
- **Overplacement** — believing you are better than the others. Measured by the four
  contests, each of which cost more to enter than an average competitor could expect to win.
- **Overprecision** — being surer than the situation allows. Measured by the pairs of
  optimistic and pessimistic values you gave.

**Why we did not say so in advance.** Naming confidence would have told you which answers
count as a flaw, and people adjust their answers when they can see what is being looked for.
We made no false statement about any of the tasks; we withheld the purpose and are explaining
it now, before you leave. This is the only thing that was held back.

Your decisions were compared with reference values stored in the study, taken from published
research and from interviews with founders. They were never shown during the session, so
nothing you saw could tell you what would have been right.
""",
}

DEBRIEF_DATA = {
    "title": "Your data",
    "body": """
Your answers are stored under the pseudonym code **{code}**, and that code is the only link
to you. Keep it if you might want your data removed.

**To withdraw your data**, write to [mail address] with your code. No reason is needed and
there is no deadline. Your data will be deleted and will not enter the analysis.

If you would rather your data were not used, you can say so now and nothing further is kept.

**One week from now** we will send you a short questionnaire, about 5 minutes. It is stored
separately from today's session and linked only by your code. It is what lets us compare
decisions with the way founders describe themselves.

Questions about the study: [name, mail address]. Ethics: [Nova SBE statement].
""",
    "withdraw": "Please do not use my data",
    "keep": "My data can be used",
}

DEBRIEF_RESULTS = {
    "title": "Your results",
    "intro": "A single session cannot diagnose anyone, and these numbers say nothing about "
             "you as a founder. They are here so you can see what your decisions were "
             "compared with.",
    "intervals_header": "The ranges you gave",
    "intervals_note": "For each question we drew one value from the reference distribution. "
                      "A well-calibrated pair of values captures it about 8 times out of 10.",
    "contests_header": "The four contests",
    "contests_note": "Each contest cost more to enter than an average competitor could "
                     "expect to win back. Entering is not a mistake, it is a bet on being "
                     "better than the others. The outcomes below were drawn after you decided.",
}

THANK_YOU_NOT_FOUNDER = """
Thank you for your interest. This study is open to founders and co-founders only, so the
session ends here. Nothing has been stored.
"""

THANK_YOU_END = """
That is everything. Thank you for the 20 minutes, and for playing it as seriously as you did.

Your code is **{code}**.
"""
