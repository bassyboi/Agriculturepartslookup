# Agriculture Parts Lookup

A collection of John Deere equipment parts data and a forum mining tool for tracking common issues and replacement parts.

## Product Folders

Each product has its own folder under `products/` containing CSV files with part numbers and common issues:

| Folder | Equipment | Description |
|--------|-----------|-------------|
| `products/cp770_cotton_picker/` | CP 770 Cotton Picker | Picking unit, air system, hydraulics, electrical, engine, basket/conveying parts |
| `products/8r_tractors/` | 8R Series Tractors | Engine, transmission (IVT/e23), axles, hydraulics, electrical, cab, guidance parts |
| `products/9r_tractors/` | 9R Series Tractors | Engine, transmission (e18/e23), drivetrain, track system (9RX), hydraulics, electrical parts |
| `products/jd1720_planter/` | JD 1720 Planter | Seed metering, vacuum system, row unit, drive system, electrical, monitoring parts |

### CSV File Structure

Each product folder contains two CSV files:

**`<model>_parts.csv`** - Complete parts listing:
- `part_number` - John Deere part number
- `part_name` - Short part name
- `category` - System category (Engine, Hydraulics, Electrical, etc.)
- `description` - Detailed part description
- `compatibility` - Compatible equipment models
- `price_usd` - Approximate price in USD

**`<model>_common_issues.csv`** - Known issues and fixes:
- `issue_id` - Unique issue identifier
- `issue_category` - System category
- `description` - Issue description
- `affected_parts` - Parts involved
- `recommended_part_numbers` - Part numbers to resolve the issue (semicolon-separated)
- `severity` - Low / Medium / High / Critical

## Forum Mining Tool

The `jd1720_forum_miner.py` script scrapes agricultural forums to identify common JD 1720 planter issues and the parts discussed in forum threads.

### Requirements

```
pip install -r requirements.txt
```

### Usage

```bash
python jd1720_forum_miner.py
```

The forum miner generates two output CSV files:
- `jd1720_threads.csv` - Per-thread analysis
- `jd1720_aggregate.csv` - Aggregated frequency data
