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

Each tractor brand folder also includes a **`<brand>_performance_parts.csv`** with ranked aftermarket performance upgrades specific to that brand's production models — ECU tunes, turbo upgrades, tires, cooling, hydraulics, guidance, and more. Every part is verified to bolt on to the production tractor.

## Precision Ag Brands

Full product catalogs and known issues for all major precision agriculture technology brands:

| Brand | Products Folder | Products | Key Categories |
|-------|----------------|----------|----------------|
| **Trimble** | `products/trimble_precision_ag/` | 15 | Displays, GNSS, auto-steer, corrections, rate control, sensors, yield monitoring |
| **Raven Industries** | `products/raven_industries/` | 12 | Displays, GNSS, auto-steer, nozzle PWM, rate control, machine vision, autonomy |
| **Ag Leader** | `products/ag_leader/` | 15 | Displays, GNSS, auto-steer, rate control, crop sensors, planter controls, yield monitoring |
| **Topcon Agriculture** | `products/topcon_agriculture/` | 12 | Displays, GNSS, auto-steer, corrections, rate control, crop sensors, boom control |
| **Precision Planting** | `products/precision_planting/` | 16 | Planter monitors, seed delivery, metering, downforce, depth, closing, fertilizer, sensing |
| **Hemisphere / Outback** | `products/hemisphere_outback/` | 10 | Displays, GNSS, auto-steer, corrections, section control, rate control |
| **Climate FieldView** | `products/climate_fieldview/` | 10 | Data collection, satellite imagery, analytics, seed advisor, yield analysis, API integration |
| **Reichhardt** | `products/reichhardt_steering/` | 10 | Auto-steer (hydraulic & motor), ISOBUS controllers, valve kits (JD/CNH/AGCO/Claas), implement steering |

### Precision Ag CSV Structure

**`<brand>_products.csv`** - Product catalog:
- `product_id` - Unique product identifier
- `product_name` - Product name
- `category` - Category (Display, Guidance, Rate Control, Sensing, etc.)
- `description` - Detailed product description
- `approx_price_usd` - Approximate price
- `tractor_compatibility` or `equipment_compatibility` - Compatible equipment
- `key_features` - Key features and capabilities
- `connectivity` - Communication protocols (CAN bus, ISOBUS, WiFi, cellular, etc.)

**`<brand>_common_issues.csv`** - Known issues and troubleshooting:
- `issue_id` - Unique issue identifier
- `issue_category` - Category (Display, GNSS, Auto-Steer, Rate Control, etc.)
- `description` - Issue description
- `affected_products` - Products involved
- `recommended_action` - Troubleshooting steps and resolution
- `severity` - Low / Medium / High / Critical

## Planter Brands

All major planter brands with parts catalogs, common issues, and ranked performance parts:

| Brand | Model | Products Folder | Row Units | Metering |
|-------|-------|-----------------|-----------|----------|
| **John Deere** | 1720 (MaxEmerge 5) | `products/jd1720_planter/` | 30 parts, 18 issues | Vacuum disc |
| **John Deere** | MaxEmerge XP (7200/7300) | `products/maximerge_xp_planter/` | 34 parts, 21 issues | Finger pickup |
| **Case IH** | 2150 Early Riser | `products/case_ih_2150_planter/` | 31 parts, 17 issues | Vacuum disc |
| **Kinze** | 3600 | `products/kinze_3600_planter/` | 30 parts, 17 issues | Brush meter |
| **Great Plains** | YP-2425A | `products/great_plains_yp2425a/` | 26 parts, 15 issues | Vacuum disc |
| **White (AGCO)** | 9800VE | `products/white_9800ve_planter/` | 26 parts, 16 issues | Vacuum / electric |
| **Monosem** | NG Plus 4 | `products/monosem_ng_plus/` | 26 parts, 16 issues | Vacuum w/ singulator |
| **Vaderstad** | Tempo V/L/F | `products/vaderstad_tempo/` | 27 parts, 16 issues | PowerShoot high-speed |

Each planter folder contains parts, common issues, and a **ranked performance parts CSV** with aftermarket upgrades (closing wheels, seed firmers, meters, downforce, row cleaners, monitors) verified to fit that planter's production row units.

## Other Equipment

| Folder | Equipment | Description |
|--------|-----------|-------------|
| `products/cp770_cotton_picker/` | CP 770 Cotton Picker | Picking unit, air system, hydraulics, electrical, engine, basket/conveying parts |

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
