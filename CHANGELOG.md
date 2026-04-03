# Changelog

## [v0.2.0] - 2026 (in progress)

### Added
- Real-ESRGAN 4x upscale pipeline for frame quality improvement
- Sync validation notebook (SoccerNet x StatsBomb)
- SYNC_OFFSET_SECONDS = 2.26s validated on El Clasico (stdev 0.09s)
- Extraction design: 4fps, 10s window, Shot/Dribble/Pass/Carry events
- PLAYER_SLUG and LEAGUE_FOLDER mappings in config.py

### Fixed
- Neymar name: 'Junior' without accent matches StatsBomb API
- Dataset updated: 28,119 events (all 6 players including Neymar)
- extractor.py: uses PLAYER_SLUG from config (no hardcoded paths)

### Data
- Neymar: 123 shots, 273 dribbles, 1,970 passes, 2,173 carries (La Liga)
- Neymar leads all 6 players in dribbles and carries

---

## [v0.1.0] - 2026

### Added
- Full setup notebook (Google Colab, sections 1-6)
- StatsBomb Open Data pipeline (La Liga + UCL 2015/16)
- SoccerNet video download pipeline (20 matches, balanced BBC/MSN)
- Shot Map visualization: BBC vs MSN - La Liga 2015/16
- Finishing Zones comparison: La Liga vs Champions League
- Preliminary key findings table (xG, goals, conversion rate)

### Dataset
- BBC: 10 La Liga + 3 UCL matches
- MSN: 10 La Liga + 1 UCL match
- 5 players with data (Neymar missing — fixed in v0.2.0)

### Known Limitations
- Neymar missing from data (name encoding bug — fixed in v0.2.0)
- StatsBomb 360 not available for 2015/16 season
- Frame-by-frame processing (no temporal context yet)
