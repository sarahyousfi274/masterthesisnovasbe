# Putting the simulation online

Three routes, in the order you will probably need them.

---

## 1 On your own machine

For playing it through yourself and for cognitive interviews, where you are sitting with
the founder anyway.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Data goes to `data/sessions.db`.

To see the data page, copy `.streamlit/secrets.toml.example` to
`.streamlit/secrets.toml`, set a password, then open
`http://localhost:8501/?view=admin`.

---

## 2 A link for a handful of beta testers

No deployment needed. Start the app as above, then in a second terminal:

```bash
cloudflared tunnel --url http://localhost:8501
```

It prints a `https://something.trycloudflare.com` address that works as long as your
machine stays on and the tunnel runs. Good for two or three testers in an afternoon.
Not for data collection over weeks.

Install cloudflared with `brew install cloudflared` on macOS or from
`https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/`.

---

## 3 Streamlit Community Cloud

**Two files decide how the app looks online.** `requirements.txt` pins Streamlit
to the exact version the app was tested with; without the pin the cloud
installs the newest release and the styling can break. `.streamlit/config.toml`
fixes the light theme and the accent color; without it Streamlit falls back to
its red default and follows the visitor's dark mode. Both must be in the
repository at exactly these paths.

### Three things to know before you start

**The repository has to be private.** Not as a preference: `sim/codebook.json` holds every
reference value and the whole measurement logic. In a public repo a participant who
searched the app's name could read what is being measured and what counts as the right
answer, which breaks R5 and the cover story.

**A private repo gives you a restricted app by default.** Streamlit takes the app's
visibility from the repository, so a private repo produces an app only invited viewers can
open. You change it back to public in the app settings, and then anyone with the link can
start a session, which is what you need for founders. Community Cloud allows one
restricted app at a time; making yours public frees that slot anyway.

**The SQLite file will not survive.** A hosted Streamlit app has no permanent disk, and it
is spun down after 12 hours without visitors. Waking it rebuilds the container and
reinstalls the dependencies, so anything written to the file system is gone. Deploying
without `DATABASE_URL` means losing data, silently.

### Steps

1. Create a **private** repository on github.com, for example `founder-sim`.
2. Upload this folder. In the browser: on the empty repo page choose *uploading an
   existing file*, then drag in everything. `.gitignore` already keeps `data/` and
   `secrets.toml` out, but when you upload through the browser check that neither is in
   the list before committing.
3. Go to `share.streamlit.io`, sign in with GitHub and choose *Create app*. Grant the
   extra permission for private repositories when it asks. Pick the repository, branch
   `main`, main file `app.py`. Give it a URL you are happy to put in a recruitment mail.
4. Open *Advanced settings* and paste your secrets:

   ```toml
   ADMIN_PASSWORD = "choose-something-long"
   DATABASE_URL = "postgresql://user:password@host:5432/dbname?sslmode=require"
   ```

   Secrets can also be edited later under *Settings* and *Secrets*. The app restarts
   when you save them.
5. Deploy. The first build takes a few minutes.
6. **Set the app to public.** In the app's settings, under sharing, switch it from
   restricted to public. Then open the link in a private browser window to confirm a
   stranger can reach it. If you skip this, every founder you invite hits a sign-in wall.
7. Check `https://your-app.streamlit.app/?view=admin`. It should ask for the password and
   then show the storage line, which must say Postgres and not SQLite.

There is no login for participants, which is what you want, and the pseudonym code is the
only identifier.

### The sleeping problem

An app with no visitors for 12 hours goes to sleep. The next person to open the link sees
a page saying the app is sleeping, with a button to wake it, and then waits 30 to 60
seconds while the container rebuilds. Pushing to the repository no longer wakes it.

For a study recruiting founders over weeks by mail this is a real dropout risk: the first
person to click each morning meets a sleep screen. Three ways round it:

- Send invitations in batches and open the app yourself shortly before, so it is awake
  when people arrive.
- Have something visit the app every few hours. A free uptime monitor pointed at the URL
  is enough, and there are ready-made GitHub Actions for it.
- Host it yourself, which removes both the sleeping and the EU question below.

### Getting a database

You need a Postgres database with a connection string. Free or near-free options that let
you choose an EU region:

- **Supabase**, region Frankfurt or Zurich. Create a project, then *Project Settings*,
  *Database*, *Connection string*, URI. Use the pooled connection ("Transaction" or
  "Session" pooler) rather than the direct one, because hosted apps open and close
  connections constantly.
- **Neon**, region Frankfurt. The connection string is on the project dashboard.
- Postgres on a small **Hetzner** server in Nuremberg or Falkenstein, if someone on the
  team is comfortable with a server.

Add `?sslmode=require` to the end of the connection string if it is not already there.

The app creates its three tables on first use. Nothing to set up in the database itself.

---

## The EU question, honestly

Section 6.1 of the thesis says data are stored in a database in the EU. An EU Postgres
satisfies that for storage at rest.

Streamlit Community Cloud itself runs in the United States. Personal data is processed on
that server while a session runs, even though it comes to rest in the EU. For pseudonymous
data this is normally handled through the provider's standard contractual clauses, but it
is a point to raise with Castro and in the ethics submission rather than to decide
yourselves. If the committee wants the whole chain in the EU, the app has to be hosted in
the EU as well, and then a small Hetzner server running the same code is the
straightforward answer. Nothing in the app changes either way.

Two things that help regardless: the pseudonym code is the only identifier in the session
data, and the mail addresses for the follow-up live in their own table, so the analysis
export carries no contact data.

---

## While collecting data

- **Download often.** The data page has one button per table. Do it after every few
  participants until you trust the setup.
- **Withdrawals by mail** go through the same page. Enter the code, press Delete, and the
  session, every answer and the contact are gone.
- **Check the storage line** on the data page after every redeploy. If it ever says
  SQLite, the secret did not load and the data will not survive.
- **Do not edit `sim/codebook.json` mid-collection.** Changing a reference value changes
  the scoring, so participants before and after would not be comparable. The codebook
  version is stored with every session, so you can see if it happened.
