# Agriculture Parts Lookup

A multi-brand agricultural equipment parts database covering tractors, planters, and specialty equipment with parts catalogs, common issues, and ranked performance upgrades verified to fit production machines.

## Tractor Brands & Classes

All major tractor brands are organized by class. The `products/tractor_classes.csv` reference file maps every brand and model line to its class, HP range, engine, transmission options, and typical use.

### Tractor Classes

| Class | HP Range | Typical Use | Brands Covered |
|-------|----------|-------------|----------------|
| **Compact Utility** | 24-130 HP | Small farm, livestock, loader work | Kubota L, Case IH Farmall |
| **Utility / Row Crop** | 110-250 HP | Mixed farming, dairy, hay, row crop | JD 6R, NH T6, Fendt 700, MF 6700S, Claas Arion 600, Kubota M7 |
| **Row Crop** | 225-435 HP | Row crop, heavy tillage, planting | JD 8R, Case IH Magnum, NH T8, Fendt 900, MF 8700S, Kubota M8, Claas Axion 900 |
| **4WD / Articulated / Track** | 370-645 HP | Heavy tillage, large-scale farming, land forming | JD 9R/9RX, Case IH Steiger/Quadtrac, NH T9/SmartTrax, Fendt 1000/MT, Challenger MT800, Versatile |

### Brand Coverage

| Brand | Model Lines | Class | Products Folder |
|-------|-------------|-------|-----------------|
| **John Deere** | 8R Series | Row Crop (230-410 HP) | `products/8r_tractors/` |
| **John Deere** | 9R / 9RT / 9RX | 4WD / Track (390-640 HP) | `products/9r_tractors/` |
| **Case IH** | Magnum | Row Crop (250-380 HP) | `products/case_ih_magnum/` |
| **Case IH** | Steiger / Quadtrac | 4WD / Track (420-620 HP) | `products/case_ih_steiger/` |
| **New Holland** | T8 | Row Crop (320-435 HP) | `products/new_holland_t8/` |
| **New Holland** | T9 / SmartTrax | 4WD / Track (435-645 HP) | `products/new_holland_t9/` |
| **Fendt** | 900 Vario | Row Crop (270-396 HP) | `products/fendt_900_vario/` |
| **Fendt** | 1000 Vario / MT | 4WD / Track (396-517 HP) | `products/fendt_1000_vario/` |
| **Massey Ferguson** | 8700S | Row Crop (270-370 HP) | `products/massey_ferguson_8700s/` |
| **Kubota** | M7 | Utility (128-170 HP) | `products/kubota_m7/` |
| **Kubota** | M8 | Row Crop (190-225 HP) | `products/kubota_m8/` |
| **Claas** | Axion 900 | Row Crop (270-410 HP) | `products/claas_axion_900/` |
| **Challenger** | MT800 | 4WD / Track (430-590 HP) | `products/challenger_mt800/` |

## Other Equipment

| Folder | Equipment | Description |
|--------|-----------|-------------|
| `products/cp770_cotton_picker/` | CP 770 Cotton Picker | Picking unit, air system, hydraulics, electrical, engine, basket/conveying parts |
| `products/jd1720_planter/` | JD 1720 Planter | Seed metering, vacuum system, row unit, drive system, electrical, monitoring parts |
| `products/maximerge_xp_planter/` | MaxEmerge XP Planter | Finger pickup meter, row units, fertilizer, transmission, drive system parts |

## Parts CSV Structure

Each product folder contains two CSV files:

**`<model>_parts.csv`** - Complete parts listing:
- `part_number` - OEM part number
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

## Tractor Performance Parts (Ranked)

The `tractor_performance_roi_analysis.py` script ranks 21 aftermarket tractor performance parts — ECU tunes, turbo upgrades, tires, hydraulics, precision ag, cooling, lighting — by ROI. **Every part is verified to fit production tractors** with no permanent modifications (bolt-on, plug-in, or drop-in only).

### Data

`products/tractor_performance_parts.csv` contains 21 performance upgrades from manufacturers including Steinbauer, AG Diesel Solutions, BorgWarner, aFe Power, Precision Planting, Firestone, Michelin, Titan, Raven, and others with:

- HP and torque gains
- Fuel efficiency improvement percentage
- Estimated ROI % and payback hours
- Tractor compatibility across all brands (JD, Case IH, NH, Fendt, MF, Kubota, Claas, Challenger)
- Production fitment verification for every part

### Performance ROI Scoring

Each part is scored on four weighted factors:

| Factor (weight) | Description |
|-----------------|-------------|
| **ROI %** (40%) | Estimated return on investment from field data |
| **Payback speed** (25%) | Inverse of payback hours — faster payback scores higher |
| **Compatibility** (20%) | Number of tractor brands/models the part fits |
| **Power gain** (15%) | HP and torque improvement (engine parts) |

Parts are tiered: **Top Tier** (score >= 70), **Strong** (>= 50), **Moderate** (>= 30), **Situational** (< 30).

### Usage

```bash
python tractor_performance_roi_analysis.py
```

### Output

- `products/tractor_performance_ranked.csv` - All parts ranked by composite performance score
- Console summary with tier breakdown, best-in-category picks, and fitment verification

### Performance Categories

| Category | Top-Ranked Product | Fits Production |
|----------|--------------------|-----------------|
| Engine / Intake | Donaldson PowerCore Air Filter | Yes — drops into factory housing |
| Engine / ECU Tuning | Power Chip Pro ECU Tune | Yes — plug-in OBD module |
| Transmission / Cooling | Derale Aux Trans Cooler | Yes — inline on factory lines |
| Tires / Traction | Firestone IF Tires | Yes — fits factory rims |
| Guidance / Steering | Outback eDriveX Auto-Steer | Yes — universal steering mount |
| Precision Ag | Raven Viper 4+ Rate Controller | Yes — ISOBUS standard |

## High-ROI Planter Performance Upgrades

The `planter_roi_analysis.py` script ranks aftermarket planter upgrades — closing wheels, seed firmers, meters, downforce systems, speed tubes, row cleaners — by their return on investment for planting performance (yield gain per dollar spent).

### Data

`products/planter_performance_upgrades.csv` contains 16 aftermarket products from Precision Planting, Martin Industries, Yetter, Copperhead Ag, Schaffert, and Ag Leader with:
- Estimated yield gain (bu/ac) from field trials
- Approximate price per row or per planter
- ROI percentage and payback acreage
- Planter compatibility (JD 1720, 7200/7300, Kinze, Case IH)

### ROI Scoring

Each upgrade is scored on four weighted factors:

| Factor (weight) | Description |
|-----------------|-------------|
| **ROI %** (40%) | Field-data estimated return on investment |
| **Revenue/ac** (30%) | Yield gain x corn price ($4.50/bu default) |
| **Payback speed** (20%) | Inverse of payback acreage — faster payback scores higher |
| **Compatibility** (10%) | Number of planter models the upgrade fits |

Products are tiered: **Top Tier** (score >= 70), **Strong** (>= 50), **Moderate** (>= 30), **Situational** (< 30).

### Usage

```bash
python planter_roi_analysis.py
```

### Output

- `products/planter_high_roi_report.csv` - All upgrades ranked by composite ROI score
- Console summary with tier breakdown and best-in-category picks

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
