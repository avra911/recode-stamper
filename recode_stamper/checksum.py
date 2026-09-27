def determine_plate_checksum_bits(total_bits: int) -> int:
    """Return the checksum bit count Recode.checksum uses for a given payload size."""

    if total_bits == 144:
        return 8

    if total_bits == 288:
        return 24

    raise ValueError(
        "total_bits must be 144 (12 plates) or 288 (24 plates)"
    )
