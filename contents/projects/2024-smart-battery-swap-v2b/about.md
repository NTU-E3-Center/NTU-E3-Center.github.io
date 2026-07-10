Taiwan has the world's densest network of electric-scooter **battery-swapping
stations** — Gogoro alone runs thousands of them. Each station holds dozens of
charged batteries that mostly sit idle between swaps: in effect, distributed energy
storage scattered across the city. Buildings, meanwhile, increasingly need
flexibility to soak up rooftop solar and trim peak grid demand on the road to
**nearly zero-energy buildings (NZEB)**. This completed NSTC project (2024–2025)
asked whether swapping stations can double as flexible energy assets for the
buildings next door, coupling the transport and building sectors.

The obstacle is real-time control. Conventional optimization — model predictive
control or mixed-integer linear programming (MILP) — produces accurate
charge/discharge schedules but is too slow and too dependent on accurate forecasts
for live operation, and operational data at any single station are sparse and
uneven. The project set out to overcome both barriers at once.

Its **Vehicle-to-Building (V2B)** framework has three parts. A **Bayesian
phase-aligned synthetic time-series generator** enriches sparse swapping-demand,
building-load, and PV records while preserving their daily rhythm and variability.
A **MILP scheduler** then computes cost-optimal charging and discharging under real
operating constraints. Finally, a **lightweight, optimization-trained neural
network** learns from those optimal schedules to reproduce near-optimal decisions
directly from the past 24 hours of data — in milliseconds, with no online
forecasting or solving. The whole pipeline was demonstrated on a Gogoro station and
an adjacent building on the National Taiwan University campus.

Against an immediate-charging baseline, the optimized V2B strategy cut building
electricity cost by about **9%**, raised on-site solar self-consumption by
**8.5%**, and lifted building energy self-sufficiency by **21%**, while the learned
controller matched the optimizer at millisecond speed. Together these results show
that battery-swapping infrastructure can act as a genuine, deployable distributed
energy resource — offering a scalable, data-efficient control path for campus
microgrids, public buildings, and future smart-energy districts, and scientific
grounding for Taiwan's distributed-energy, smart-grid, and net-zero-city goals.
