"""Every word a participant sees, plus the effect table that drives the story.

Kept deliberately separate from codebook.json: this file is the story, which
participants experience, and the codebook holds the hidden reference values.

Rules for this file
- Nothing names confidence, calibration or overconfidence.
- No benchmark that could serve as an answer appears anywhere. The scientific
  background of a question is shown on hover over a small link icon, by author
  and year only, never with titles or content.
- Text can use {name} (the startup's name), {industry} (a short industry label),
  {runway} and {launch_budget}. app.fill() supplies them.
- American English, "startup", typographic apostrophes.
"""

APP_VERSION = "0.14.2"

# --------------------------------------------------------------------------
# Contact details. Replace the study address once the team mailbox exists.
# --------------------------------------------------------------------------

CONTACT_EMAIL = "decisions-in-founding@outlook.com"
STARTUP_NAME = "Lumora"          # the fictional startup every participant runs
WITHDRAWAL_WEEKS = 4

# --------------------------------------------------------------------------
# Starting situation and the economics of the story
# --------------------------------------------------------------------------
# Net burn = monthly costs − monthly revenue. Revenue follows the number of
# customers at a fixed average revenue per customer (90 customers ≈ €8,000).

REVENUE_PER_CUSTOMER = 8_000 / 90
COST_PER_HIRE = 5_000            # monthly cost of each new team member


def joining_label(planned: int, head_of_sales: int) -> str:
    """Report line when the people hired in the Team area start."""
    hires = f"{planned} planned hire" + ("" if planned == 1 else "s")
    if planned and head_of_sales:
        return f"New team members start: {hires} and the Head of Sales"
    if planned:
        return f"New team members start: {hires}"
    return "The Head of Sales starts"
SHORT_RUNWAY_MONTHS = 6          # below this, the team feels it (morale −1)
FINANCE_START_RUNWAY = 6         # Finance starts from at least this runway (round 3, A11)

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
    "fundraise_left": None,      # runway left when the round starts (F1)
    "f4_route": None,            # loan, safe or priced (F4)
    "deferred": [],              # outcome effects held back until the final report
    "finance_bridge": 0,         # bridge from existing investors before Finance (A11)
}

STATUS_FIELDS = [
    # key, label, help text
    ("cash", "Cash", "Money in the bank right now."),
    ("burn", "Net burn per month", "Monthly costs minus monthly revenue: what the "
                                   "startup loses each month. Costs cover salaries, "
                                   "the freelancers who help run the pilot, tools "
                                   "and office."),
    ("runway", "Runway", "How many months the cash lasts. Cash divided by net "
                         "burn per month."),
    ("revenue", "Revenue per month", "Recurring revenue from paying customers."),
    ("customers", "Customers", "Paying customers using the product today."),
    ("team_size", "Team", "People working in the startup, you and your "
                          "co-founder included."),
    ("pending_hires", "Planned hires", "People you plan to hire. They join at the "
                                       "end of the Team area."),
    ("ownership", "Founders’ ownership", "Share of the company held by you and "
                                         "your co-founder together."),
    ("morale", "Team morale", "Mood of the team, from 1 (very low) to 5 (very "
                              "high). 3 is neutral."),
    ("market_confidence", "Market confidence", "How positive the signals from "
                                               "customers, press and investors "
                                               "are, from 1 (very low) to 5 "
                                               "(very high). 3 is neutral."),
]

# Labels that change for a solo founder.
STATUS_SOLO = {
    "team_size": ("Team", "People working in the startup, you included."),
    "ownership": ("Your ownership", "Share of the company you hold."),
    "morale": ("Morale", "Your drive and that of anyone who joins you, from 1 "
                         "(very low) to 5 (very high). 3 is neutral."),
}


def status_fields(solo: bool) -> list[tuple[str, str, str]]:
    """STATUS_FIELDS with the solo-founder labels where they apply."""
    if not solo:
        return STATUS_FIELDS
    return [(k, *STATUS_SOLO[k]) if k in STATUS_SOLO else (k, lab, h)
            for k, lab, h in STATUS_FIELDS]

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

# What Lumora does, one generic sentence per industry. Shown on the company
# card. "Other" uses the participant's own words.
INDUSTRY_PRODUCTS = {
    "Software and SaaS": "software that helps small businesses plan and run their "
                         "daily work",
    "Marketplace or e-commerce": "an online marketplace where independent shops sell "
                                 "to customers across Europe",
    "Fintech or insurtech": "an app that helps small businesses manage invoices and "
                            "cash flow",
    "Health and life sciences": "software that helps clinics stay in touch with "
                                "their patients between visits",
    "Industrial, hardware or deep tech": "software that connects machine sensors in "
                                         "small factories and flags problems early",
    "Consumer products or services": "an app through which households subscribe to "
                                     "the everyday products they need",
    "Energy, mobility or climate": "software that helps companies measure and cut "
                                   "their energy use",
    "Education": "an online learning platform that companies use to train their "
                 "staff",
    "Food and beverages": "an app that organizes healthy lunch orders for offices",
    "Media and entertainment": "a platform that helps independent creators run paid "
                               "communities",
}
PRODUCT_OTHER = "a new digital product in {label} for its first customers"

COMPANY = {
    "founded": "Founded last year · based in Europe",
    "product": "{name} builds {product}.",
    "run_solo": "Run by you",
    "run_team": "Run by you and your co-founder",
}

# Labels of the reports and the numbers panel (no month labels, review B3).
H4_SECOND_ROUND = {"label": "Head of Sales: after the second round, the candidate with "
                            "the stronger work sample is hired",
                   "delta": {"team_size": 1, "costs": 7000}}
BRIDGE_LABEL = "Bridge from existing investors"
BRIDGE_SENTENCE = ("Your existing investors have bridged {name} with {bridge} so that the "
                   "financing decisions start from 6 months of runway.")
HUD_CAPTION = "At the start of this area"
HUD_CAPTION_FINAL = "At the start of this round"
AREA_REPORT = {
    "veil": "End of this area", "veil_body": "Closing the books for {name}",
    "eyebrow": "Area {n} of 4 complete", "title": "Where things stand",
    "changes": "What changed in this area",
}
# Outcomes held back during the session (customers, revenue, morale, market
# confidence) are shown here, after K1 (review A9).
FINAL_REPORT = {
    "veil": "Final report", "veil_body": "How {name} has done",
    "eyebrow": "Final round complete", "title": "Final report",
    "body": "Some effects of your decisions take time to show: new customers, the "
            "mood of the team, the signals from the market and the open decisions "
            "of juries, panels and candidates. This is where {name} stands now that "
            "they have played out.",
    "changes": "What your decisions led to",
}
NO_DIRECT_COST = "no direct cost"
F1_NOTE = "planned"

# Decisions that arrive as an email. The sender is an institution or a role,
# never a named or pictured person, so no persona colors the answer (B6).
MESSAGES = {
    "T5": {"from": "Mentor", "subject": "Pitch contest: I put {name} forward",
           "body": "Hi {name} team, I have put {name} forward for a pitch contest. "
                   "Ten startups are invited, and an independent jury will rank all "
                   "ten plans."},
    "F5": {"from": "Accelerator program", "subject": "{name} is on our shortlist",
           "body": "Hi {name} team, {name} is one of 10 startups on our shortlist "
                   "for a single place in our program. An independent panel will "
                   "pick one of the ten."},
    "H5": {"from": "Head of Product candidate",
           "subject": "My decision between 10 offers",
           "body": "Hi {name} team, thank you for our conversations. I have offers "
                   "from 10 startups, {name} among them, and I will choose one of "
                   "them in the coming weeks."},
    "G5": {"from": "Procurement, potential customer", "subject": "Call for proposals",
           "body": "Hi {name} team, we are putting a contract out to tender. Ten "
                   "startups, {name} among them, are invited to submit a proposal, "
                   "and an independent panel will pick the best one."},
    "K1": {"from": "Founders’ network", "subject": "Grant raffle among 10 startups",
           "body": "Hi {name} team, we are raffling a grant of {prize} among 10 "
                   "startups. The winner is drawn by lot, so the quality of the "
                   "startups plays no role."},
}
EMAIL_SIGNOFF = "Best regards"
SOLO_GREETING = "Hi there,"          # emails to a solo founder (round 3, A8)

JOURNEY = {
    "title": "Your time at {name}",
    # The sentence about the follow-up (review A7) is in END, on the same page.
    "body": "The decisions you made, area by area.",
    "after_areas": "After the four areas",
    "final": "Where {name} stands now",
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
SECTION_FINAL = "Final round"
SECTION_INTRO_DONE = "Introduction"     # the three sections before the simulation, once done
SECTION_WRAP = "Wrap-up"

# --------------------------------------------------------------------------
# Welcome and consent
# --------------------------------------------------------------------------

CONSENT = {
    "title": "Decisions in founding",
    "lead": "A simulation study for founders, run by master’s students at Nova "
            "School of Business and Economics.",
    "facts": [
        ("About 20 minutes", "Please complete it in one sitting, on any device"),
        ("A fictional startup", "No right or wrong answers"),
        ("One short follow-up", "A single email in about a week, with a 5\u2011minute questionnaire"),
    ],
    # Text of the team, 21 October 2026. Lines in a body are separated by "\n".
    "sections": [
        ("Who we are",
         "We are Eléonore Konsbruck, Amie Weidemann and Sarah Yousfi, master’s "
         "students at Nova SBE. This study is part of our master’s thesis on how "
         "founders make decisions, supervised by Professor João Castro."),
        ("What you will do",
         "You run a fictional startup and make the decisions its founders face. "
         "Nothing you enter is checked against your real company."),
        ("Taking part is voluntary",
         f"You can have your data removed within {WITHDRAWAL_WEEKS} weeks by "
         f"writing to {CONTACT_EMAIL}. You do not need to give a reason. We will "
         "then delete your answers and your email address."),
        ("Your data",
         "Your email address is stored separately from your answers. Your answers "
         "are analyzed only in aggregate and used only for this research project. "
         "All data stays within our research team and is never shared with anyone "
         "outside it."),
        ("Questions?",
         f"Write to {CONTACT_EMAIL} or contact one of us directly:\n"
         "Eléonore Konsbruck · 66998@novasbe.pt\n"
         "Amie Weidemann · 67899@novasbe.pt\n"
         "Sarah Yousfi · 70987@novasbe.pt"),
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
    "body": "We need your email address for one short follow-up: about a week "
            "from now we send you a single email with a 5-minute questionnaire, "
            "and your address links its answers to today’s. We will not contact "
            "you for anything else. Your address is stored separately from your "
            "answers and never shared outside the research team.",
    "label": "Email",
    "placeholder": "you@example.com",
}

# --------------------------------------------------------------------------
# About you (not part of the simulation)
# --------------------------------------------------------------------------

ABOUT_NOTE = "This section is about you."
ABOUT_BANNER = ("A few questions about you and your company. The simulation will "
                "start soon.")
OTHER_LABEL = "Please specify"
# Sliders in "About you" start on this empty position, so nothing is
# preselected; the answer counts only once the handle has been moved.
SLIDER_EMPTY = "–"
SLIDER_HINT = "Drag the handle to your answer."

PROFILE = {
    "question": "About you and your company",
    "body": "We ask these questions so we can interpret the results of the "
            "simulation better, for example by experience or stage of the "
            "company. If you no longer run a company, answer for the most recent "
            "one. Your answers are never published individually.",
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
     "kind": "slider", "options": ["0", "1", "2", "3 or more"]},
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
    "body": "Count everything across your career, not only your current company. "
            "Drag each handle to your answer.",
}
EXPERIENCE_FIELDS = [
    {"key": "exp_financing",
     "label": "Times you have raised external financing (investors, loans or grants)",
     "options": ["0", "1", "2", "3", "4", "5 or more"]},
    {"key": "exp_teams", "label": "Founding teams you have been part of",
     "options": ["1", "2", "3", "4 or more"]},
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
    "body": "Three questions about your general attitude. Drag each handle to a "
            "point on the scale.",
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
         "Cash, runway and team change with your choices. You see your current "
         "status at the start and end of each area. Some effects take longer to "
         "show and appear in a final report."),
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
    "question": "Your startup: {name}",
    "body": "{name} is a young digital startup. Its first paying customers use a pilot "
            "that the team still runs largely by hand. Before you take over, decide "
            "how you run it and which industry it is in.",
    "team_label": "Do you run {name} on your own or with a co-founder?",
    "team_options": [("solo", "On my own, as the solo founder"),
                     ("team", "Together with a co-founder")],
    "team_help": "Cash, costs and customers at the start are the same either way.",
    "industry_label": "Which industry is {name} in?",
    "industry_help": "Pick the industry you know best. In every industry, {name}’s "
                     "product is digital: software, an app or an online platform.",
    "industry_placeholder": "–",
}

TRANSITION = {
    "eyebrow": "Get ready",
    "title": "Your simulation starts now",
    "body": "From here on, you run a startup. Every decision changes its numbers.",
    "button": "Enter the simulation",
}

STARTING_SITUATION = {
    "title": "Your starting situation",
    "body": "This is where you and your co-founder take over {name}. The numbers "
            "change with your decisions, and you see your current status at the "
            "start and end of each area. New customers start paying after a free "
            "trial, so revenue changes only later; you will see it in the final "
            "report. Hover over or tap the (i) next to a label to see what it means.",
    "body_solo": "This is where you take over {name}. The numbers change with "
                 "your decisions, and you see your current status at the start "
                 "and end of each area. New customers start paying after a free "
                 "trial, so revenue changes only later; you will see it in the "
                 "final report. Hover over or tap the (i) next to a label to see "
                 "what it means.",
    "button": "Continue",
}

# --------------------------------------------------------------------------
# The four domain blocks
# --------------------------------------------------------------------------
# "sequence" nodes keep their order because each builds on the one before.
# "units" are groups that stay together (the rank question comes right before
# its contest) and are inserted at a random position. The two attention checks
# are placed by flow.py into the second and third area of the track. With
# "outcome_last", the last node of the sequence (F4, H4, G4) is the outcome the
# earlier answers should predict, so nothing is inserted after it.

BLOCKS = {
    "team": {
        "title": "Building the product",
        "intro": "Your first customers pay for a pilot that you still run largely "
                 "by hand. You and your co-founder have agreed to turn it into a "
                 "first real product, the minimum viable product (MVP). The next "
                 "decisions are about how you get it done.",
        "intro_solo": "Your first customers pay for a pilot that you still run "
                      "largely by hand. You have decided to turn it into a first "
                      "real product, the minimum viable product (MVP). The next "
                      "decisions are about how you get it done.",
        "sequence": ["T3", "T1"],     # T3 first: T1 names weeks of founder time
        "units": [["T5", "T2"]],
    },
    "finance": {
        "title": "Finance",
        "intro": "{name} loses money every month until revenue covers the costs. "
                 "The next decisions are about financing.",
        "sequence": ["F3", "F4"],     # F1 is the opening decision (see OPENING)
        "outcome_last": True,         # F4 is the outcome node, always last
        "units": [["F5", "F2"]],
    },
    "hiring": {
        "title": "Team",
        "intro": "The work is outgrowing what you and your co-founder can do. The "
                 "next decisions are about who joins and when.",
        "intro_solo": "The work is outgrowing what you can do alone. The next "
                      "decisions are about who joins and when.",
        "sequence": ["H3", "H1", "H4"],   # H3 first: H1 frames "3 months"
        "outcome_last": True,
        "units": [["H5", "H2"]],
    },
    "gtm": {
        "title": "Go-to-market",
        "intro": "{name} is ready enough to sell. The next decisions are about "
                 "how you reach customers.",
        "sequence": ["G1", "G3", "G4"],
        "outcome_last": True,
        "units": [["G5", "G2"]],
    },
}

# Building the product always comes first. The other three areas form a Latin
# square: across the three tracks each of them appears once in position 2, 3
# and 4, so position effects (fatigue, learning, the state of the company) are
# spread evenly over the areas and can be tested with track as a factor.
TRACKS = {
    1: ["team", "finance", "hiring", "gtm"],
    2: ["team", "gtm", "finance", "hiring"],
    3: ["team", "hiring", "gtm", "finance"],
}

ATTENTION_CHECKS = ["AC1", "AC2"]      # into areas 2 and 3 of every track
FINAL_ROUND = ["K1"]
# Opening decision right after the starting situation, the same for everyone.
# F1 needs the full runway (14 months) so all four options are feasible in
# every track; in the Finance area it would come too late in Track 3.
OPENING = ["F1"]
OPENING_EYEBROW = "Your first decision"
HUD_CAPTION_OPENING = "Your starting position"                    # after all four areas, same for everyone

FINAL_INTRO = {
    "title": "One more decision",
    "body": "Before you finish, one last opportunity comes up for {name}.",
}

# Open threads of the contests. While the session runs, the area report shows
# only that a decision is pending. The outcome is drawn with the stated chance
# (1 in 10, 1 in 8 with the upgrade) and shown in the final report after K1,
# when every measured decision has been made, so it cannot change later answers.
CONTEST_STORY = {
    "T2": {"label": "Pitch contest", "pending": "the jury announces the winner later",
           "won": "Lumora wins the pitch contest", "lost": "Another startup wins the pitch contest",
           "effect": "cash"},
    "F2": {"label": "Accelerator place", "pending": "the panel decides later",
           "won": "Lumora gets the accelerator place", "lost": "The accelerator picks another startup",
           "effect": "cash"},
    "H2": {"label": "Head of Product", "pending": "she decides in the coming weeks",
           "won": "The Head of Product chooses Lumora: the saved search is worth €40,000",
           "lost": "The Head of Product chooses another startup", "effect": "cash"},
    "G2": {"label": "Customer tender", "pending": "the panel picks the winner later",
           "won": "Lumora wins the customer contract", "lost": "The customer picks another proposal",
           "effect": "cash"},
    "K1": {"label": "Grant raffle", "pending": "the draw takes place later",
           "won": "Lumora’s entry is drawn", "lost": "Another startup’s entry is drawn",
           "effect": "cash"},
}
CONTEST_RESULTS_TITLE = "How the open decisions turned out"
CONTEST_NOT_ENTERED = "not entered"

# Removed with the review of 20 October: the contests are fictional, so no
# results are promised anywhere.
CONTEST_NOTE = ""

# Scientific background, shown on hover over the link icon, author and year only.
BG_CONTEST = ["Camerer & Lovallo (1999)", "Cain, Moore & Haran (2015)"]
BG_RANK = ["Moore & Healy (2008)", "Benoît, Dubra & Moore (2015)"]

# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------

SCREENS = {

    # ------------------------------------------------------- Building the product
    "T1": {
        "kind": "choice",
        "question": "The MVP of {name} has 5 core features. How much of the "
                    "development do you and your co-founder do yourselves?",
        "question_solo": "The MVP of {name} has 5 core features. How much of the "
                         "development do you do yourself?",
        "body": "Work you two do yourselves costs no cash but takes your time "
                "away from fundraising, hiring and sales. External developers are "
                "paid from your cash.",
        "body_solo": "Work you do yourself costs no cash but takes your time away "
                     "from fundraising, hiring and sales. External developers are "
                     "paid from your cash.",
        "background": ["Buehler, Griffin & Ross (1994)", "Kahneman & Lovallo (1993)"],
        "event": "MVP development",
        "options": [
            {"key": "A", "label": "Everything ourselves",
             "label_solo": "Everything myself",
             "extra": "no cash cost · about 16 weeks of founder time",
             "extra_solo": "no cash cost · about 32 weeks of your time",
             "effects": {"morale": -1}},
            {"key": "B", "label": "About three quarters ourselves, the rest to "
                                  "freelancers",
             "label_solo": "About three quarters myself, the rest to freelancers",
             "extra": "€6,000 · about 12 weeks of founder time",
             "extra_solo": "€6,000 · about 24 weeks of your time",
             "effects": {"cash": -6_000}},
            {"key": "C", "label": "About half to external developers",
             "extra": "€12,000 · about 8 weeks of founder time",
             "extra_solo": "€12,000 · about 16 weeks of your time",
             "effects": {"cash": -12_000}},
            {"key": "D", "label": "Almost everything to external developers",
             "extra": "€20,000 · about 3 weeks of founder time",
             "extra_solo": "€20,000 · about 6 weeks of your time",
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
        "background": ["Jørgensen, Teigen & Moløkken (2004)", "Soll & Klayman (2004)"],
        "unit": "weeks",
        "optimistic_is_high": False,
        "low_help": "Only 1 in 10 similar projects would be ready sooner.",
        "high_help": "Only 1 in 10 similar projects would take longer.",
        "min_value": 1, "max_value": 400, "step": 1,
    },

    # ----------------------------------------------------------------- Finance
    "F1": {
        "kind": "choice",
        "question": "When do you and your co-founder start fundraising?",
        "question_solo": "When do you start fundraising?",
        "body": "{name} has {runway_text} of runway. Starting means preparing the "
                "deck and contacting investors. Until then, {name} keeps paying its "
                "running costs from the cash it has.",
        "background": ["Buehler, Griffin & Ross (1994)", "Kahneman & Lovallo (1993)"],
        "event": "Fundraising starts",
        # Asked in remaining runway. Only options below the current runway are
        # shown; "Right away" always. The runway left at the start is stored as
        # numeric_value and scored against 9 months (codebook reference_rule).
        "remaining_runway": True,
        "options": [
            {"key": "A", "label": "Right away, with {runway_text} left",
             "remaining": None, "effects": {}},
            {"key": "B", "label": "When 9 months of runway are left",
             "remaining": 9, "effects": {}},
            {"key": "C", "label": "When 6 months are left",
             "remaining": 6, "effects": {}},
            {"key": "D", "label": "When 3 months are left",
             "remaining": 3, "effects": {"market_confidence": -1}},
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
        "question": "Investors will ask {name}, an early-stage {industry} startup, "
                    "for a revenue forecast. Monthly revenue is {revenue_now} today. "
                    "What will monthly revenue be in 12 months?",
        "background": ["Cassar (2010)", "Soll & Klayman (2004)"],
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
        "background": ["Malmendier & Tate (2005)", "Malmendier, Tate & Yan (2011)"],
        "event": "Financing",
        "options": [
            {"key": "A", "label": "Bank loan over 24 months at 9 percent",
             "extra": "about €13,700 per month in repayments, no equity given up",
             "effects": {"raise": 300_000, "costs": 13_700, "f4_route": "loan"}},
            {"key": "B", "label": "SAFE (simple agreement for future equity) with "
                                  "a €6 million valuation cap",
             "extra": "up to 5% of the company, final stake set in the next round",
             "effects": {"raise": 300_000, "ownership": -5, "f4_route": "safe"}},
            {"key": "C", "label": "Priced round: 5% of the company for €300,000",
             "extra": "the investor joins as a board observer, about €15,000 in "
                      "legal costs",
             "effects": {"raise": 285_000, "ownership": -5,
                         "market_confidence": 1, "f4_route": "priced"}},
        ],
    },

    # --------------------------------------------------------------------- Team
    "H1": {
        "kind": "choice",
        "display": "pills",
        "question": "How many people do you plan to have hired within the next 3 "
                    "months?",
        "body": "Each new hire adds about €5,000 to the monthly costs. In the numbers, "
                "everyone you plan to hire is counted from the end of this area.",
        "background": ["Buehler, Griffin & Ross (1994)", "Kahneman & Lovallo (1993)"],
        "event": "Hires planned",
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
        "question": "An experienced Head of Product is choosing between offers from "
                    "10 startups, {name} among them.",
        "body": "Before you decide whether to make an offer: if she ranked all 10 "
                "startups by how attractive they are to her, where would {name} "
                "land?",
        "background": BG_RANK,
    },

    "H2": {
        "kind": "contest",
        "question": "Do you make the Head of Product an offer?",
        "body": "If she joins you, you save 3 months of searching, worth {prize}. "
                "Preparing a standard offer, with an assessment day and employer "
                "branding, costs {base_cost}. An average startup has a 1 in 10 "
                "chance of being her choice.",
        "background": BG_CONTEST,
        "event": "Offer to Head of Product",
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
        "question": "You start searching for a senior backend engineer today: a "
                    "full-time, permanent role, without an external recruiter. How "
                    "many weeks until a contract is signed?",
        "background": ["Soll & Klayman (2004)", "Ben-David, Graham & Harvey (2013)"],
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
                 "person in the interview and gave you and your co-founder a very "
                 "strong gut feeling",
        },
        "candidates_solo": {
            "A": "scored 82 of 100 on a structured work sample and has solid "
                 "references",
            "B": "scored 71 of 100 on the work sample but was the most convincing "
                 "person in the interview and gave you a very strong gut feeling",
        },
        "after": "This role comes on top of the hires you planned. Either hire adds "
                 "€7,000 to the monthly costs and joins at the end of this area.",
        "background": ["Kausel, Culbertson & Madrid (2016)", "Dawes, Faust & Meehl (1989)"],
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
        "body": "Your <b>first channel</b> is the one you and your co-founder "
                "believe in most, based on talks with early customers. The rest "
                "goes into small tests of two or three other channels to see which "
                "ones work.",
        "body_solo": "Your <b>first channel</b> is the one you believe in most, "
                     "based on talks with early customers. The rest goes into small "
                     "tests of two or three other channels to see which ones work.",
        "background": ["Koning, Hasan & Chatterji (2022)", "Berman & Van den Bulte (2022)"],
        "event": "Launch budget",
        "options": [
            {"key": "A", "label": "100% first channel, no tests",
             "effects": {"spend_launch_budget": True, "customers": 45,
                         "market_confidence": -1}},
            {"key": "B", "label": "70% first channel, 30% tests",
             "effects": {"spend_launch_budget": True, "customers": 45}},
            {"key": "C", "label": "40% first channel, 60% tests",
             "effects": {"spend_launch_budget": True, "customers": 45,
                         "market_confidence": 1}},
            {"key": "D", "label": "20% first channel, 80% tests",
             "effects": {"spend_launch_budget": True, "customers": 45,
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
        "background": ["Camerer & Lovallo (1999)", "Moore, Oesch & Zietsma (2007)"],
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
        "question": "Suppose a new paid sales channel brings {name} 9, 16 and 21 new "
                    "paying customers in its first three months. How many new "
                    "paying customers will it bring in month 9?",
        "background": ["O’Connor & Lawrence (1989)", "Soll & Klayman (2004)"],
        "unit": "customers",
        "optimistic_is_high": True,
        "low_help": "Only 1 in 10 comparable channels would bring fewer in month 9.",
        "high_help": "Only 1 in 10 comparable channels would bring more in month 9.",
        "min_value": 0, "max_value": 100_000, "step": 1,
    },

    "G4": {
        "kind": "choice",
        "question": "One month after the launch, the first channel has brought "
                    "{name} about 30% fewer new customers than planned. At the same "
                    "time, several new customers came through a channel you had not "
                    "focused on. What do you do next month?",
        "background": ["Chen et al. (2024)", "Kirtley & O’Mahony (2023)"],
        "event": "After the first month",
        "options": [
            {"key": "A", "label": "Stay the course: the first channel needs more time",
             "effects": {"customers": 15}},
            {"key": "B", "label": "Sharpen the first channel with new messaging, same "
                                  "budget",
             "effects": {"customers": 15}},
            {"key": "C", "label": "Run a four-week test comparing both channels",
             "effects": {"customers": 15}},
            {"key": "D", "label": "Move most of the budget to the new channel now",
             "effects": {"customers": 15}},
        ],
    },
    # -------------------------------------------------------------- Final round
    "K1": {
        "kind": "contest",
        "message": True,                 # text in MESSAGES["K1"]
        "question": "Do you enter the raffle?",
        "body": "Entering costs {base_cost}. Every entry has a 1 in 10 chance of "
                "winning.",
        "background": ["Camerer & Lovallo (1999)"],
        "event": "Grant raffle",
        "options": [
            {"key": "A", "label": "Do not enter"},
            {"key": "B", "label": "Enter the raffle"},
            {"key": "C", "label": "Enter with a premium entry",
             "extra": "raises the chance to 1 in 8"},
        ],
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
CHART_REVENUE = [("3 months before", 7_320, None), ("2 months before", 7_470, "+2%"),
                 ("1 month before", 7_770, "+4%"), ("When you took over", 8_000, "+3%")]
CHART_REVENUE_CAPTION = "Monthly revenue in the months before you took over"
# Shorter axis labels for phones up to 480 px wide (0.14.2).
CHART_SHORT_LABELS = {"3 months before": "3 mo before", "2 months before": "2 mo before",
                      "1 month before": "1 mo before", "When you took over": "At takeover",
                      "In 12 months": "In 12 mo"}
CHART_CUSTOMERS = [("Month 1", 9, None), ("Month 2", 16, None),
                   ("Month 3", 21, None)]

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
            "**In about a week** we will send you one more email with a short "
            "questionnaire of about 5 minutes. It is the only email you will get from "
            "us, and it also explains what the study was about.",
}

THANK_YOU_NOT_FOUNDER = (
    "Thank you for your interest. This study is open to founders and "
    "co-founders only, so the session ends here. Nothing has been stored."
)

CLOSE = {
    "button": "Continue",
    "title": "You can close this page now.",
    "body": "Your answers have been saved. Thank you again for taking part.",
}

ALREADY_TOOK_PART = {
    "title": "Thank you",
    "body": "A response has already been submitted with this email address, so you "
            "cannot take part a second time. Thank you very much for your interest "
            f"and your time. If you think this is a mistake, write to\u00a0{CONTACT_EMAIL}.",
    "close": "You can close this page now.",
}

# A1 (0.14.0): an earlier, unfinished session with the same email address.
RESUME_OFFER = {
    "question": "Welcome back",
    "body": "You started this study earlier with this email address. Do you want to "
            "continue where you stopped?",
    "continue": "Continue where I stopped",
    "restart": "Start again",
    "gone": "The earlier session can no longer be continued. Please start again.",
}

# 0.14.2: a resume link opened again after a longer break.
RESUME_CHECK = {
    "title": "Welcome back",
    "body": "To continue where you stopped, please enter the email address you gave "
            "at the start. This keeps your answers safe if the link was passed on.",
    "continue": "Continue where I stopped",
    "restart": "Start a new session instead",
    "wrong": "This email address does not match this session. Please check it, or "
             "start a new session.",
}

DECLINED = "No problem. Nothing has been stored. You can close this page."
