# YNAB Amazon Spend for Home Assistant

A custom Home Assistant integration that creates monetary sensors for net Amazon
spend over rolling 1-, 7-, 30-, and 365-day windows.

## Install with HACS

1. In HACS, open the three-dot menu and choose **Custom repositories**.
2. Add `https://github.com/terhorst/ha-mwoa` with category **Integration**.
3. Find **YNAB Amazon Spend** in HACS and install it.
4. Restart Home Assistant.

## Configure

Add this to `configuration.yaml`:

```yaml
ynab_amazon_spend:
  token: !secret ynab_pat
  plan_id: last-used
  match_terms:
    - amazon
    - amzn
```

Restart Home Assistant. The YAML is imported as a config entry and four sensors
are created. `plan_id` can instead be a YNAB plan UUID. `match_terms` are matched
case-insensitively against the transaction payee and memo.

Alternatively, after restarting, add **YNAB Amazon Spend** from **Settings →
Devices & services → Add integration** and enter the token in the UI.

YNAB stores outflows as negative amounts. The sensors expose positive spending;
refunds reduce the total. Deleted transactions and transfers are excluded.

The API is polled hourly by default. Set `scan_interval` in YAML to change it.
