# Changelog

## [v0.1.0] - 2025

### Added
- Full project setup notebook (Sections 1-6)
- StatsBomb Open Data integration (La Liga + UCL 2015/16)
- SoccerNet video download pipeline (20 matches, balanced BBC/MSN)
- 6 source scripts: config, loader, extractor, classifier, merger, visualizer
- Shot Map visualization: BBC vs MSN - La Liga 2015/16
- Finishing Zones comparison: La Liga vs Champions League
- Preliminary key findings table (xG, goals, conversion rate)
- Dataset: 23,767 events (La Liga) + 554 events (UCL)

### Data
- BBC: 10 La Liga + 3 UCL matches
- MSN: 10 La Liga + 1 UCL match
- Players: Bale, Benzema, Cristiano, Messi, Neymar, Suarez

### Known Limitations
- Neymar missing from UCL data (StatsBomb open data coverage)
- StatsBomb 360 not available for 2015/16 season
- Frame-by-frame processing (no temporal context yet)
