# FASTING

[![image](https://img.shields.io/pypi/v/fasting.svg)](https://pypi.python.org/pypi/fasting)
[![image](https://github.com/jbpauly/fasting/workflows/docs/badge.svg)](https://jbpauly.github.io/fasting)
[![image](https://github.com/jbpauly/fasting/workflows/build/badge.svg)](https://github.com/jbpauly/fasting/actions?query=workflow%3Abuild)
[![image](https://img.shields.io/twitter/follow/j_b_pauly?style=social)](https://twitter.com/j_b_pauly)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A Python package to  interact with fasting logs from apps like Zero.**

-   Free software: MIT license
-   Documentation: https://jbpauly.github.io/fasting

## Background & Motivation
### Fasting
Fasting is a technique used to improve metabolic health, reduce inflammation, rebalance gut health, lose weight, increase longevity, improve mental clarity and focus.
There's various forms of fasting, with **Intermittent Fasting (IF)** likely being the most common. You can read about **IF** and other types of fasting on the [Zero blog](https://www.zerofasting.com/which-type-of-fasting-is-right-for-you/).
During extended periods of fasting,
our bodies ["flip a metabolic switch"](https://www.zerofasting.com/intermittent-fasting-may-improve-metabolic-syndrome/)
from burning glucose to burning fatty acids and ketones.
> The metabolic switch typically takes place in a later phase of fasting,
> when the glycogen stores contained in the liver are depleted and adipose tissue (fat) begins to increase fatty
> acids and glycerol. While the switch generally occurs between 12 and 36 hours after stopping eating,
> it can depend upon the total liver glycogen content when the person started the fast, as well as the person’s
> energy expenditures during the fast.

Josh Clemente, a Levels co-founder, has shared the benefits of IF on his metabolic fitness on the
[Levels blog](https://www.levelshealth.com/blog/12-glucose-lowering-strategies-to-improve-metabolic-fitness#w-node-cb8068197b2d-1eb46bd3:~:text=Explore%20intermittent%20fasting).
>  During periods of extended fasts, Josh's average glucose gently trends down into the optimal range and remains there
> with only 2-3% variation for days at a time.

### Digital Biomarker Pipeline
This package is part of the [**Digital Biomarker Discovery Pipeline (DBDP)**](https://dbdp.org/).

![DBDP](https://dbdp.org/assets/dbdp/DBDP_logo_2.jpg)

You can read more about the DBDP [here](https://medium.com/digital-biomarker-discovery/digital-biomarker-discovery-pipeline-fbfe75cdd9a4).
If you track your fasts, there's a chance you also track biomarkers with wearables and other hardware in the modern health stack.
The goal of this package is to enable you to utilize _**your**_ data for your own purpose, like cross analyzing
 fasting performance with other biomarkers.

### Original Use Case
Functionality around fasting logs was originally built for the
**Metabolic Health Analysis** [app](https://share.streamlit.io/jbpauly/glucose-sleep-analysis/main/src/app.py).

![Metabolic Health Analysis](https://raw.githubusercontent.com/jbpauly/glucose-sleep-analysis/main/src/content/analysis.gif)

Part of the app's software was pulled out and enhanced to create this stand-alone
[FASTING](https://github.com/jbpauly/fasting) package.
Checkout the app [repo](https://github.com/jbpauly/glucose-sleep-analysis)
and the [DBDP](https://dbdp.org/) for ideas and use cases around your own biomarker analysis.

## Usage and Features
This section provides a quick preview of some of the package features.
Check out the full [API documentation](https://jbpauly.github.io/fasting/quantify/)
and _getting started_ [tutorial](https://jbpauly.github.io/fasting/tutorials/tutorial_getting_started/)
for more information.

### Installation
This package is supported by Python 3.7+.
```
pip install fasting
```

### Standardize Log Format

**Export format from Zero:**

|Date   |Start|End  |Hours|Night Eating|
|-------|-----|-----|-----|------------|
|1/17/21|19:15|12:00|16   |1           |
|1/16/21|19:45|10:14|14   |2           |
|1/15/21|21:00|10:00|13   |3           |

**Discrete Logs:**

```
discrete_logs = fasting.quantify.zero_fasts(zero_export.csv)
```

| fast | start_dt            | end_dt              |
|------|---------------------|---------------------|
| 0    | 2021-01-14 19:00:00 | 2021-01-15 11:22:00 |
| 1    | 2021-01-15 21:00:00 | 2021-01-16 10:00:00 |
| 2    | 2021-01-16 19:45:00 | 2021-01-17 10:14:00 |

**Continuous Log:**

```
continuous_log = fasting.quantify.continuous_fasts(discrete_logs)
```

| datetime            | fasting status |
|---------------------|----------------|
| 2021-01-14 19:00:00 | 1              |
| 2021-01-14 19:01:00 | 1              |
| 2021-01-14 19:02:00 | 1              |

### Fasting Metrics
```
cumulative_hours = quantify.daily_cumulative_hours(continuous_log)
max_consecutive_hours = quantify.daily_max_consecutive_hours(continuous_log)
```
![Metrics](https://raw.githubusercontent.com/jbpauly/glucose-sleep-analysis/main/src/content/data/fast_breakdown.jpg)

## Fasting Resources
### Blogs and Apps
- [Zero](https://www.zerofasting.com/blog/)
- [Do Fasting](https://dofasting.com/what-is-intermittent-fasting)
- [Levels Health](https://www.levelshealth.com/blog)
- [Found My Fitness](https://www.foundmyfitness.com/topics/fasting)

### Studies
#### [Study 1](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6627766/)
Impact of time restricted feeding (TRF) on metabolic health
- Two groups
    - Group 1: 6 hour feeding window (8am-2pm), TRF group
    - Group 2: 12 hour feeding window (8am-8pm), control group
- Overweight, non-diabetic individuals

**Result / Findings**:
- Engaging in time restricted feeding for just 4 days can lower fasting glucose, fasting insulin, and mean glucose
 levels significantly
- TRF group demonstrated lower post meal glucose spikes, despite eating the same meals

#### [Study 2](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/99309EE4738FC8BA4AB29843B44AC2C9/S0007114511006507a.pdf/div-class-title-effect-of-meal-timing-and-glycaemic-index-on-glucose-control-and-insulin-secretion-in-healthy-volunteers-div.pdf)
Relationship between time of day of eating and metabolic health

**Result / Findings**:
Eating food later in the evening will cause significant increase in insulin and glucose levels compared to eating the same meal in the morning

#### [Study 3](https://casereports.bmj.com/content/casereports/2018/bcr-2017-221854.full.pdf)
Impact of IF on controlling type 2 diabetes
- 3 participants with type 2 diabetes
- 24 hour fasts 3-4 days per week

**Result / Findings**:
- All participants meaningfully reversed diabetes in as little as 7 months
- One participant regained enough insulin sensitivity to get off high doses of insulin medication within 3 weeks

## Credits
This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
