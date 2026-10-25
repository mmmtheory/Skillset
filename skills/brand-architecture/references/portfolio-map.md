# Portfolio map format

Write the map as JSON (or YAML if PyYAML is installed) so `scripts/portfolio_check.py` can check it.

```json
{
  "masterbrand": "Acme",
  "model": "hybrid",
  "brands": [
    {"name": "Acme", "tier": "masterbrand"},
    {"name": "Acme Ledger", "tier": "sub-brand", "parent": "Acme", "relationship": "sub-brand", "audience": "small businesses"},
    {"name": "Tally", "tier": "brand", "parent": "Acme", "relationship": "endorsed", "endorsement": "Tally, by Acme", "audience": "accountants"},
    {"name": "Nimbus", "tier": "brand", "parent": "Acme", "relationship": "house-of-brands", "audience": "enterprise"},
    {"name": "automatic tax filing", "tier": "feature", "parent": "Acme Ledger"}
  ]
}
```

| Field | Values |
| --- | --- |
| `tier` | `masterbrand`, `brand`, `sub-brand`, `product`, `feature` |
| `relationship` | `branded-house`, `sub-brand`, `endorsed`, `house-of-brands`, `feature` |
| `parent` | name of another entry; the masterbrand has none |
| `endorsement` | required for `endorsed` |
| `audience` | free text, used in the reasoning, not by the script |

Present the map to people as an indented tree or a Mermaid diagram:

```
Acme
├── Acme Ledger (sub-brand)
│   └── automatic tax filing (feature)
├── Tally, by Acme (endorsed)
└── Nimbus (separate)
```
