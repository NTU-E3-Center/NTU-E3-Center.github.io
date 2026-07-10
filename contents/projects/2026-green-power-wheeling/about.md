Taiwan's export industries — ICT, semiconductors, metalworking — increasingly
live or die on their access to certified green power. RE100 commitments from
Apple, Google, and Microsoft, together with the EU's CBAM carbon border levy,
have turned renewable procurement from a corporate-responsibility bonus into a
hard market threshold. Yet Taiwan runs an isolated grid, and solar's
intermittency produces a sharpening "duck curve": midday PV floods the system
while the evening peak arrives after the sun is gone. As the market shifts from
feed-in tariffs toward free trading and corporate power-purchase agreements,
green power has become a scarce, tradable asset — and premium supply is largely
locked up by large firms, leaving smaller users unable to buy, or unable to
absorb their own surplus.

The renewable-energy retailer sits between generation and demand, and as wheeling
(轉供) scales up, its allocation problem gets genuinely hard. Green-power wheeling
is not bulk trading; it is a dynamic game among intermittent generation,
fluctuating load, and Taipower's 15-minute settlement rule, played out across
many generators and many consumers at once. Worse, most users hand over only
monthly bills, so the retailer plans under real information asymmetry — over-commit
and lose money, or stay conservative and miss the business. This project,
commissioned by **GREENET (天能綠電)** and led by Prof. I-Yun Lisa Hsieh, treats
wheeling as a multi-objective optimization problem — one that must satisfy
regulatory rules, contractual promises, and profit at the same time — and builds
a decision-support system around it.

The system is assembled from four modules. A **demand-simulation** module turns a
user's sparse monthly bill (peak / half-peak / off-peak totals) into a
high-fidelity 15-minute load curve, using load-shape logic for four archetypal
users — a 24-hour factory, a weekday office, an all-week storefront, and an
evening-and-weekend department store. A **settlement engine** encodes Taipower's
official wheeling rules (Article 13 of the wheeling and direct-supply operating
regulations) into verifiable logic: a first-pass 15-minute match taking the lesser
of generation and demand, then a second-pass reallocation of surplus within the
same price period, with standardized settlement reports. An **optimization** core
then searches the multi-generator-to-multi-consumer matching space — tens of
thousands of possible configurations — for the pairing that maximizes wheeling
gross profit (or, switchably, total wheeled volume), under practical controls such
as surplus-ratio thresholds and fixed-contract locks. Finally, a
**flexible-allocation** module anticipates Taipower's sandbox program, letting the
same engine switch between today's 15-minute matching and a parameterized,
priority-weighted allocation for future policy scenarios.

Validated against Taipower's standard test cases, the system aims to replace slow,
error-prone manual spreadsheeting with a repeatable, auditable, data-driven
workflow: pre-contract risk assessment from simulated demand, compliant automated
settlement, and profit-maximizing allocation that trims generation-side surplus
and consumption-side shortfall alike. For the E3 Center, it carries its
energy-systems and techno-economic modelling into the fast-moving business of
green-power retail — and aims to leave behind a replicable technical benchmark for
Taiwan's renewable-energy trading sector.
