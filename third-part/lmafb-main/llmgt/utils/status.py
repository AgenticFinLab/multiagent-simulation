"""
Status enums for market simulation components.
"""


class InvestorStatus:
    """
    All status enums for investor components.
    """
    # The status of an investor's message reception from market.
    WELL_RECEIVED = "All Market Message Received"
    PARTIAL_RECEIVED = "Partial Market Message Received-{}"
    NO_RECEIVED = "No Market Message Received"
    # The overall running state of the investor.
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATED = "terminated"
    # The alert/issue status for the investor.
    NONE = "no_alert"
    DELAYED = "Delayed Response-{}"
    HIGH_VOLATILITY = "High Volatility-{}"
    DATA_ANOMALY = "Data Anomaly-{}"
    CONSTRAINT_CONFLICT = "constraint_conflict"
    INVESTOR_ERROR = "investor_error"


class MarketStatus:
    """
    All status enums for market components.
    """
    # The status of the market's message reception from investors.
    WELL_RECEIVED = "All Investor Messages Received"
    PARTIAL_RECEIVED = "Partial Investor Messages Received-{}"
    NO_RECEIVED = "No Investor Messages Received"
    # The overall running state of the market.
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATED = "terminated"
    # The alert/issue status for the market.
    NONE = "no_alert"
    DELAYED = "Delayed Response-{}"
    HIGH_VOLATILITY = "High Market Volatility-{}"
    DATA_ANOMALY = "Data Anomaly-{}"
    CONSTRAINT_CONFLICT = "constraint_conflict"
    MARKET_ERROR = "market_error"


class SimulatorStatus:
    """
    All status enums for simulator components.
    """
    # The status of simulator's connection to actors.
    WELL_RECEIVED = "All Actors Connected"
    PARTIAL_RECEIVED = "Partial Actors Connected-{}"
    NO_RECEIVED = "No Actors Connected"
    # The overall running state of the simulator.
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    TERMINATED = "terminated"
    # The alert/issue status for the simulator.
    NONE = "no_alert"
    DELAYED = "Delayed Response-{}"
    CONNECTION_ERROR = "Connection Error-{}"
    DATA_ANOMALY = "Data Anomaly-{}"
    SIMULATION_ERROR = "simulation_error"
