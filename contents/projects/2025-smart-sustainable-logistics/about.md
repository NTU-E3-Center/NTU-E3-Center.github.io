Reaching net zero in freight hinges on the **last mile** — the high-frequency,
stop-heavy final leg from depot to customer that is among the most polluting and
least efficient parts of any supply chain. **Cold-chain** last-mile delivery is
harder still: refrigerated trucks burn fuel both to move and to stay cold, yet most
Green Vehicle Routing Problem (GVRP) studies simplify away the very things that
drive emissions — real traffic speeds, road gradients, refrigeration load, and
refrigerant leakage.

This three-year project builds a **data-driven, emission-aware GVRP** that closes
that gap, in partnership with a Taiwanese third-party logistics (3PL) operator.

**Path-level emission modeling.** Rather than approximating emissions from
straight-line distance, the framework estimates them along the actual driven path.
Vehicle-propulsion emissions use the **Comprehensive Modal Emissions Model (CMEM)**
— sensitive to speed, load, and gradient — while refrigeration load (ASHRAE-based)
and **R404A refrigerant leakage** are modeled explicitly. Real **traffic-speed
profiles** and **continuous road elevation** come from the Google Directions and
Elevation APIs, with cubic-spline smoothing to strip tunnel and bridge artifacts.

**Solved at real scale.** The problem is cast as an energy-minimizing GVRP and
solved with a custom **Adaptive Large Neighborhood Search (ALNS)** metaheuristic,
validated on a real northern-Taiwan cold-chain network — **223 convenience stores**
served from a single Ruifang distribution centre, where a ~100 m elevation drop into
the Taipei basin makes terrain genuinely matter.

**A three-year arc.** Year one (above) establishes the last-mile, single-objective
foundation. Year two extends to a **bi-objective** model — carbon *and* operating
cost, with a marginal-abatement-cost lens — and to **first-mile** pickup-and-
scheduling. Year three integrates both into a **two-echelon (2E-GVRP)** network and
brings in **AI-assisted optimization** — reinforcement learning and learning-based
methods — for large-scale, dynamic routing.
