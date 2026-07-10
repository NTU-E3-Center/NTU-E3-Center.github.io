Green hydrogen is one of the more promising ways to connect renewable power to
the parts of decarbonization that electrons alone struggle to reach — heavy
industry, long-duration storage, and hard-to-electrify transport. Wind is an
attractive power source for the electrolyzers that split water into hydrogen, but
wind is also random, seasonal, and volatile, and that volatility propagates
straight into hydrogen's cost, reliability, and scalability. In the chain from
wind power to green hydrogen, how well you can *see the wind coming* sets a
ceiling on how efficiently the electrolyzer can run — which is why this project,
commissioned by the **Metal Industries Research & Development Centre (MIRDC)** and
led by Prof. I-Yun Lisa Hsieh, treats wind forecasting as the critical front-end
capability.

Accurate wind-power forecasts do two jobs here. They translate directly into the
power available to the electrolyzer, and therefore into how much hydrogen can be
made and at what levelized cost (LCOH); and they are the basis on which an
energy-management system schedules the electrolyzer's start-ups, shut-downs, and
operating points — decisions whose losses and equipment wear depend on knowing the
wind input in advance. But forecasting wind well is genuinely hard: wind fields
carry strong small-scale turbulence and non-stationarity, terrain (roughness,
obstacles, local eddies) makes them spatially uneven, and a turbine's own control
— yaw, blade pitch, rotor inertia, power-curve switching — turns wind speed into
power output through a highly nonlinear, time-lagged mapping.

The project answers with a two-tier forecasting architecture. A **short-term**
layer (hourly-to-daily) builds a regional meteorological background field from
ground weather stations and produces day-ahead wind-power forecasts, correcting
turbine power curves for environmental effects to sharpen the wind-speed-to-power
step. An **ultra-short-term** layer (minute-scale, roughly 15–30 minutes ahead)
captures fast wind-field behavior — gusts and direction shifts — models the
turbine's response delay, and updates continuously from high-frequency SCADA
telemetry and live weather data. Throughout, the system carries **uncertainty
quantification** — prediction intervals, probability estimates, and multi-model
ensembles — so its outputs come with confidence indicators for risk-aware
dispatch, and it converts forecast reserve power into a first estimate of the
electrolyzer's real-time hydrogen-production cost under varying load.

Beyond the standalone forecasts, the work is designed to plug into a larger
wind–hydrogen–storage picture: it validates against MIRDC's planned pilot site,
hands its wind outputs to hydrogen-cost and energy-management modules, and lays
groundwork for a coupled wind-to-hydrogen decision tool that could scale across
multiple wind farms and sites. For the E3 Center, it extends the group's
renewable-forecasting line — building on its earlier work on deep-learning
wind-power prediction and the economics of offshore-wind hydrogen — toward the
front end of Taiwan's emerging green-hydrogen supply chain.
