"""Constants for YNAB Amazon Spend."""

DOMAIN = "ynab_amazon_spend"
PLATFORMS = ["sensor"]

CONF_TOKEN = "token"
CONF_PLAN_ID = "plan_id"
CONF_MATCH_TERMS = "match_terms"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_PLAN_ID = "last-used"
DEFAULT_MATCH_TERMS = ["amazon", "amzn"]
DEFAULT_SCAN_INTERVAL = 3600

API_BASE = "https://api.ynab.com/v1"

WINDOWS = {
    "day": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}
