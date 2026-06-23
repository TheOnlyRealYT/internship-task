import pytest
from backend.services.dedup import validate_record_enums

async def test_invalid_asset_type_raises_clean_error():
    record = {"asset_type": "not_a_real_type", "value": "x.com"}
    with pytest.raises(ValueError, match="Invalid"):
        validate_record_enums(record)