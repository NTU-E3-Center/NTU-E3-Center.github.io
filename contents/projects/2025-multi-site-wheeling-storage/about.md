Meeting corporate net-zero targets — RE100, ESG disclosure, green-supply-chain
rules — increasingly hinges on **how** a company sources and routes renewable
electricity, not just how much it buys. In Taiwan's green-power market, "wheeling"
(轉供) allocates renewable attributes by contract rather than physical flow, which
leaves companies with two persistent problems: **generation and demand rarely line
up in time**, and **multiple sites with different load profiles are hard to
coordinate** — so one site curtails surplus solar while another buys extra
certificates to cover a shortfall.

Run with industry partner <strong><a href="https://www.nextdrive.io" target="_blank" rel="noopener">NextDrive Inc. (聯齊科技)</a></strong> under the NSTC
Industry–Academia program, this project builds a **data-driven, resilient
optimization model** that dispatches green-power wheeling, rooftop solar, and
battery storage across a company's sites as a single system — from the
*electricity buyer's* perspective rather than a single building's.

**The model.** The problem is formulated as **Mixed-Integer Linear Programming**
(Python · CVXPY · HiGHS solver). Decision variables span grid (brown) and
purchased-green power, cross-site solar wheeling (BGES), PV self-use and battery
charging, storage charge/discharge with a binary no-simultaneous guard and
state-of-charge tracking, and a two-tier over-contract-capacity penalty. The
objective minimises total operating cost — energy purchases plus tiered demand
penalties — with a deliberately tiny wheeling-cost coefficient that nudges the
model to share power internally before buying from the grid. Constraints enforce
power balance, renewable conservation with **self-use priority**, storage limits,
a minimum renewable-share (RE%) threshold per site, and a no-self-wheeling rule.

**The data.** The model was validated on a full year (May 2024 – April 2025) of
**15-minute** load and solar data — 35,040 timesteps — from three heterogeneous
sites of a northern-Taiwan corporate group: a daytime **office** (184 kW contract,
rooftop PV + storage), an all-day high-load **mall** (1,730 kW, the main
green-power consumer), and a **warehouse** whose 3,400 kWp of solar far exceeds its
own flat load, letting it act as a **virtual power plant** and the group's main
supplier.

Backtested against a no-dispatch baseline, the optimized model cut grid reliance,
held every site under its contracted capacity all year, and lowered the group's
total bill while accumulating renewable-energy certificates — with results framed
as deployable recommendations for integration into NextDrive's energy-management
platform.
