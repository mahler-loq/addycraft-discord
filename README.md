# AddyCraft Discord Bot

Developed by: Mahler von Loqerlien

Deployed/Hosted by: Adzel Firestar
## How to deploy:

Open a terminal on your (preferrably linux) machine and paste:
```
git clone https://github.com/mahler-loq/addycraft-discord
cd addycraft-discord
python3 -m venv pyvenv
source pyvenv/bin/activate
pip install -r requirements.txt
```
Now with `python3 main.py`, you will be able to deploy the bot, STDOUT/STDERR can be forwarded to a logfile if desired.
It is recommended to adjust `./config.py` before a first run

## Particular Files:

- `src/cogs/dummy.py` -> Template for new cogs
- `src/cnst.py` -> Hardcoded constants
- `src/helpers.py` -> Helper function
- `config.py` -> Global configuration


## Breakdown of the project's root dir
```
./
├── main.py
├── ongoing_work_notes.md
├── README.md
├── requirements.txt
└── src
```
- `main.py` -> main script, starts the dance party
- `ongoing_work_notes.md` -> self explainatory (me ranting about what i have to do next)
- `requirements.txt` dependency list (PIP)
- `src/` -> the actual source files :)

THIS FILE IS UNFINISHED!!!