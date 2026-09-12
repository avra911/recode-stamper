import pytest

from recode import Recode, words


def test_basic_round_trip_12():
    r = Recode(words)
    secret = "MyPassword123!"
    mnemonic = r.encode(secret.encode("utf-8"))
    assert len(mnemonic) == 12
    assert r.decode(mnemonic).decode("utf-8") == secret


def test_basic_round_trip_24():
    r = Recode(words)
    secret = "MyVeryLongPassword1234567890!"
    mnemonic = r.encode(secret.encode("utf-8"))
    assert len(mnemonic) == 24
    assert r.decode(mnemonic).decode("utf-8") == secret


def test_all_lengths_0_to_32():
    r = Recode(words)
    for length in range(33):
        data = b"A" * length
        assert r.decode(r.encode(data)) == data


def test_rejects_data_too_long():
    r = Recode(words)
    try:
        r.encode(b"A" * 33)
        raise AssertionError("Expected ValueError for 33-byte payload")
    except ValueError:
        pass

    try:
        r.encode(b"A" * 17, plates=12)
        raise AssertionError("Expected ValueError for 17-byte payload with 12 plates")
    except ValueError:
        pass


def test_invalid_checksum_is_detected():
    r = Recode(words)
    mnemonic = list(r.encode(b"abc"))
    index = r.word_to_index[mnemonic[1]]
    mnemonic[1] = r.words[(index + 1) % r.WORD_COUNT]

    with pytest.raises(ValueError):
        r.decode(mnemonic)


def test_unknown_word_rejected():
    r = Recode(words)
    try:
        r.decode(["__not_a_word__"])
        raise AssertionError("Expected unknown word to fail")
    except ValueError:
        pass


def test_all_lengths_use_expected_plate_count():
    r = Recode(words)
    for length in range(33):
        data = bytes((i % 256) for i in range(length))
        mnemonic = r.encode(data)
        expected_plates = 12 if length <= 16 else 24
        assert len(mnemonic) == expected_plates
        assert r.decode(mnemonic) == data


def test_rejects_invalid_plate_count():
    r = Recode(words)
    mnemonic_12 = r.encode(b"a")

    with pytest.raises(ValueError, match="plates must be exactly 12 or 24"):
        r.decode(mnemonic_12[:11])

    with pytest.raises(ValueError, match="plates must be exactly 12 or 24"):
        r.decode(["word"] * 13)

    with pytest.raises(ValueError, match="plates must be exactly 12 or 24"):
        r.encode(b"a", plates=13)


def test_exact_capacity_12_and_24():
    r = Recode(words)
    data_12 = b"A" * 16
    data_24 = b"B" * 32

    m12 = r.encode(data_12, plates=12)
    m24 = r.encode(data_24, plates=24)

    assert len(m12) == 12
    assert len(m24) == 24
    assert r.decode(m12) == data_12
    assert r.decode(m24) == data_24


def test_rejects_invalid_padding():
    r = Recode(words)
    mnemonic = list(r.encode(b"abc", plates=12))
    index = r.word_to_index[mnemonic[-1]]
    mnemonic[-1] = r.words[(index + 1) % r.WORD_COUNT]

    with pytest.raises(ValueError, match="INVALID PADDING"):
        r.decode(mnemonic)


def test_rejects_wrong_wordlist():
    r = Recode(words)
    wrong_words = words.copy()
    wrong_words[0], wrong_words[1] = wrong_words[1], wrong_words[0]
    wrong_recode = Recode(wrong_words)

    with pytest.raises(ValueError):
        wrong_recode.decode(r.encode(b"abc"))


def test_forces_24_plates_for_short_data():
    r = Recode(words)
    secret = b"abc"
    mnemonic = r.encode(secret, plates=24)
    assert len(mnemonic) == 24
    assert r.decode(mnemonic) == secret


def test_decode_skips_prompt_when_plates_are_specified(monkeypatch):
    import recode_stamper

    mnemonic = recode_stamper.r.encode(b"secret", plates=12)

    def fail_prompt():
        raise AssertionError("decode should not ask for word count when --plates is provided")

    monkeypatch.setattr(recode_stamper, "prompt_mnemonic_input", fail_prompt)
    monkeypatch.setattr(recode_stamper.getpass, "getpass", fail_prompt)

    result = recode_stamper.main(["--decode", "--plates", "12", " ".join(mnemonic)])
    assert result == 0
