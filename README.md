# BBC vs MSN - Tactical Action Classifier

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/petersonantonio-science/bbc-vs-msn-classifier/blob/main/notebooks/BBC_vs_MSN_Setup.ipynb) [![StatsBomb Data](https://img.shields.io/badge/data-StatsBomb-red)](https://github.com/statsbomb/open-data) [![SoccerNet](https://img.shields.io/badge/video-SoccerNet-blue)](https://www.soccer-net.org/) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Comparative analysis of decision patterns and technical actions
between the two greatest attacking trios in recent football history,
using **Moondream 3** + **StatsBomb Open Data** + **SoccerNet**.

> Open source portfolio project — Peterson Antonio

---

## The Central Question

**Do the decision patterns of BBC and MSN change when
the context shifts from a league campaign (La Liga) to
a European knockout stage (Champions League)?**

Same players. Same season. Different pressure.

---

## The Players

| BBC - Real Madrid | MSN - Barcelona |
|---|---|
| Gareth Frank Bale | Lionel Andres Messi Cuccittini |
| Karim Benzema | Neymar da Silva Santos Junior |
| Cristiano Ronaldo dos Santos Aveiro | Luis Alberto Suarez Diaz |

---

## Historical Context

**La Liga 2015/16** - One of the most competitive seasons in history:
Barcelona (91 pts), Real Madrid (90) and Atletico (88)
separated by just 3 points.

**Champions League 2015/16** - Real Madrid eliminated
Manchester City in the quarterfinals and Atletico in the semis.
Barcelona fell to Atletico in the semifinals.
BBC and MSN never faced each other in the UCL that season,
making the comparison even more interesting.

---

## Data Sources

| Dataset | Usage | Access |
|---|---|---|
| StatsBomb Open Data | Events, coordinates, xG, pressure | Free |
| SoccerNet | Match videos | Free (NDA required) |
| Moondream 3 | Technical action classification | Open Source |

---

## Dataset

| Competition | BBC Matches | MSN Matches | Events |
|---|---|---|---|
| La Liga 2015/16 | 10 | 10 | 23,767 |
| UCL 2015/16 | 3 | 1* | 554 |

*Limited StatsBomb open data coverage for UCL 2015/16 - see Limitations.

---

## Architecture

```
StatsBomb Open Data (La Liga + UCL 2015/16)
        |
Filter events for all 6 players
        |
For each event -> timestamp + x,y coordinates + xG
        |
SoccerNet -> video frame at that timestamp
        |
Moondream 3 -> classify technical action
        ("left-foot shot", "dribble under pressure", etc.)
        |
Merge: tactical context (StatsBomb) + technical classification (Moondream)
        |
BBC vs MSN comparison by decision pattern
```

---

## Quick Start

### Option 1 - Google Colab (recommended)
Click the badge at the top to open the setup notebook directly in Colab.
Run sections 1 to 6 in order.

### Option 2 - Local

**1. Request SoccerNet access**
Visit [soccer-net.org](https://www.soccer-net.org/),
fill out the form and wait for the email with your password.

**2. Set up your password**
Create `soccernet_key.txt` in the project root with only the password:

    your_password_here

**3. Install dependencies**

    pip install -r requirements.txt

**4. Run the setup notebook**
Open `notebooks/BBC_vs_MSN_Setup.ipynb` and run sections 1 to 6.

---

## Project Structure

```
bbc-vs-msn-classifier/
|- src/
|  |- config.py        # Player names, paths, constants
|  |- loader.py        # Load and filter StatsBomb data
|  |- extractor.py     # Extract frames with FFmpeg
|  |- classifier.py    # Classify actions with Moondream 3
|  |- merger.py        # Merge StatsBomb + Moondream
|  |- visualizer.py    # Pitch plots with mplsoccer
|- notebooks/
|  |- BBC_vs_MSN_Setup.ipynb   # Full setup notebook
|- data/
|  |- statsbomb/       # Event and match data (CSV)
|  |- frames/          # Extracted frames (not versioned)
|  |- annotations/     # JSON annotations
|  |- raw/             # SoccerNet videos (not versioned)
|- results/
|  |- pitch_plots/     # Shot maps and heatmaps
|  |- comparisons/     # BBC vs MSN comparisons
|- requirements.txt
|- .gitignore
|- README.md
```

---

## Sample Results

### Shot Map - La Liga 2015/16
![Shot Map](results/pitch_plots/laliga/bbc_vs_msn_shotmap_laliga.png)

### Finishing Zones - La Liga vs UCL
![Finishing Zones](results/comparisons/bbc_vs_msn_zonas_finalizacao.png)

---

## Key Findings (Preliminary)

| Player | Shots | Goals | Total xG | Avg xG | Conversion |
|---|---|---|---|---|---|
| Cristiano Ronaldo | 235 | 36 | 33.4 | 0.142 | 15.3% |
| Luis Suarez | 139 | 40 | 27.6 | 0.199 | 28.8% |
| Lionel Messi | 158 | 26 | 21.3 | 0.135 | 16.5% |
| Karim Benzema | 100 | 24 | 18.1 | 0.181 | 24.0% |
| Gareth Bale | 91 | 20 | 10.3 | 0.113 | 22.0% |

*Neymar Jr. had no data available in the StatsBomb open dataset for UCL 2015/16.

---

## Honest Limitations

**1. No automatic player identification**
Moondream 3 classifies actions, not identities.
Clips are manually segmented by player.

**2. Neymar missing from UCL data**
StatsBomb open data does not include Barcelona UCL 2015/16
matches where Neymar appears in the available splits.

**3. Limited UCL coverage**
Only 1 Barcelona match and 3 Real Madrid matches available
in StatsBomb open data for UCL 2015/16.

**4. No StatsBomb 360 for 2015/16**
Freeze frames with all player positions are not available
in the free tier for this season.

**5. Frame-by-frame processing**
Moondream has no memory between frames.
Temporal context must be assembled externally.

---

## Roadmap

- [ ] Frame extraction from SoccerNet videos
- [ ] Action classification with Moondream 3
- [ ] Fine-tuning with annotated dataset
- [ ] Interactive web visualization
- [ ] Extension to 2022 FIFA World Cup (Messi, Cristiano and Modric)

---

## Stack

| Tool | Usage |
|---|---|
| Moondream 3 | Technical action classification |
| statsbombpy | StatsBomb Open Data access |
| SoccerNet | Video download |
| FFmpeg | Frame extraction |
| OpenCV | Image preprocessing |
| mplsoccer | Pitch plots and visualizations |
| Pandas | Dataset structuring |

---

## References

- [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- [SoccerNet](https://www.soccer-net.org)
- [Moondream 3](https://moondream.ai/blog/moondream-3-preview)
- [mplsoccer](https://mplsoccer.readthedocs.io)
- [statsbombpy](https://github.com/statsbomb/statsbombpy)

---

## License & Credits

- StatsBomb data: non-commercial use, attribution required
- SoccerNet videos: non-commercial use, NDA signed
- Original videos are NOT included in this repository
- Only annotation JSONs and code are versioned

*Data source: StatsBomb Open Data - statsbomb.com*