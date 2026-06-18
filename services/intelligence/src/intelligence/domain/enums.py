from __future__ import annotations

from enum import StrEnum


class BillingModel(StrEnum):
    FIXED_FEE = "fixedFee"
    PERCENT_OF_COST = "percentOfCost"
    TIME_AND_MATERIALS = "timeAndMaterials"
