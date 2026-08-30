"""
How to run:

  python recode.py --encode "test!"
  python recode.py --decode "africa eatery gloved cupid brevity aardvark aardvark aardvark aardvark aardvark aardvark aardvark"

  python recode.py encode "MyPassword123!"
  python recode.py decode "artist scavenge intimate airdrop humdrum curfew hexagon candy comedy bunion brevity aardvark"

  python recode.py

The script encodes UTF-8 text into a 12- or 24-word mnemonic and decodes it back.
"""

import argparse
import hashlib
from pathlib import Path


class Recode:
    """
    RECODE FORMAT
    =============

    Wordlist:
        Exactly 4096 unique words.
        Each word represents exactly 12 bits.

    12 plates:
        144 bits total
        8 bits   = data length
        8 bits   = checksum
        128 bits = data + zero padding

        Maximum data: 16 bytes

    24 plates:
        288 bits total
        8 bits   = data length
        24 bits  = checksum
        256 bits = data + zero padding

        Maximum data: 32 bytes

    Automatic selection:
        0..16 bytes  -> 12 plates
        17..32 bytes -> 24 plates
        33+ bytes    -> ERROR

    The mnemonic is always exactly 12 or 24 words.
    """

    WORD_COUNT = 4096
    WORD_BITS = 12

    VALID_PLATES = (12, 24)

    FORMAT = {
        12: {
            "length_bits": 8,
            "checksum_bits": 8,
            "data_bits": 128,
        },
        24: {
            "length_bits": 8,
            "checksum_bits": 24,
            "data_bits": 256,
        },
    }

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(self, words):

        # --------------------------------------------------
        # Validate wordlist size
        # --------------------------------------------------

        if len(words) != self.WORD_COUNT:
            raise ValueError(
                f"Expected exactly {self.WORD_COUNT} words, "
                f"got {len(words)}"
            )

        # Normalize words
        self.words = [
            word.strip().lower()
            for word in words
        ]

        # --------------------------------------------------
        # Validate words
        # --------------------------------------------------

        if any(not word for word in self.words):
            raise ValueError(
                "Wordlist contains an empty word"
            )

        if len(set(self.words)) != self.WORD_COUNT:
            raise ValueError(
                "Wordlist contains duplicate words"
            )

        # --------------------------------------------------
        # Create canonical wordlist fingerprint
        #
        # Each word is followed by \n so that word boundaries
        # are unambiguous.
        # --------------------------------------------------

        h = hashlib.sha256()

        for word in self.words:
            h.update(
                word.encode("utf-8")
            )
            h.update(b"\n")

        self.words_checksum = h.digest()

        # --------------------------------------------------
        # Word -> index
        # --------------------------------------------------

        self.word_to_index = {
            word: index
            for index, word in enumerate(self.words)
        }

    # ======================================================
    # BASIC HELPERS
    # ======================================================

    def index_to_bits(self, index):
        """
        Convert a word index 0..4095 into exactly 12 bits.
        """

        if not isinstance(index, int):
            raise TypeError(
                "index must be an integer"
            )

        if not 0 <= index < self.WORD_COUNT:
            raise ValueError(
                f"Invalid word index: {index}"
            )

        return format(
            index,
            "012b"
        )

    def bits_to_index(self, bits):
        """
        Convert exactly 12 bits into a word index.
        """

        if len(bits) != self.WORD_BITS:
            raise ValueError(
                "Expected exactly 12 bits"
            )

        if any(
            bit not in "01"
            for bit in bits
        ):
            raise ValueError(
                "Bits must contain only 0 or 1"
            )

        return int(bits, 2)

    # ======================================================
    # FORMAT HELPERS
    # ======================================================

    def max_data_bytes(self, plates):
        """
        Maximum data capacity for a given format.
        """

        if plates not in self.VALID_PLATES:
            raise ValueError(
                "plates must be exactly 12 or 24"
            )

        return (
            self.FORMAT[plates]["data_bits"]
            // 8
        )

    def validate_plates(self, plates):
        """
        Validate that plates is exactly 12 or 24.
        """

        if plates not in self.VALID_PLATES:
            raise ValueError(
                "plates must be exactly 12 or 24"
            )

    # ======================================================
    # CHECKSUM
    # ======================================================

    def checksum(
        self,
        data,
        length,
        checksum_bits,
    ):
        """
        Calculate checksum.

        Input to SHA-256:

            domain separator
            length
            data
            wordlist fingerprint

        The wordlist fingerprint binds the mnemonic
        to the exact ordered wordlist.
        """

        if not isinstance(data, bytes):
            raise TypeError(
                "data must be bytes"
            )

        if not 0 <= length <= 255:
            raise ValueError(
                "length must fit into 8 bits"
            )

        if length != len(data):
            raise ValueError(
                "length does not match data length"
            )

        if checksum_bits not in (8, 24):
            raise ValueError(
                "checksum_bits must be 8 or 24"
            )

        h = hashlib.sha256()

        # Explicit domain separator
        h.update(b"RECODE-V1")

        # Length
        h.update(
            bytes([length])
        )

        # Data
        h.update(data)

        # Exact wordlist fingerprint
        h.update(
            self.words_checksum
        )

        digest = h.digest()

        # Number of bytes needed
        checksum_bytes = (
            checksum_bits // 8
        )

        value = int.from_bytes(
            digest[:checksum_bytes],
            "big"
        )

        return format(
            value,
            f"0{checksum_bits}b"
        )

    # ======================================================
    # ENCODE
    # ======================================================

    def encode(self, data, plates=None):
        """
        Encode bytes into exactly 12 or 24 words.

        plates=None:
            Automatically select the smallest format.

        plates=12:
            Exactly 12 words.

        plates=24:
            Exactly 24 words.
        """

        if not isinstance(data, bytes):
            raise TypeError(
                "data must be bytes"
            )

        # --------------------------------------------------
        # Automatic format selection
        # --------------------------------------------------

        if plates is None:

            if len(data) <= self.max_data_bytes(12):
                plates = 12

            elif len(data) <= self.max_data_bytes(24):
                plates = 24

            else:
                raise ValueError(
                    f"Data too long: {len(data)} bytes. "
                    f"Maximum is "
                    f"{self.max_data_bytes(24)} bytes."
                )

        # --------------------------------------------------
        # Validate requested format
        # --------------------------------------------------

        self.validate_plates(plates)

        fmt = self.FORMAT[plates]

        max_bytes = (
            fmt["data_bits"] // 8
        )

        # --------------------------------------------------
        # Validate capacity
        # --------------------------------------------------

        if len(data) > max_bytes:
            raise ValueError(
                f"{plates} plates support maximum "
                f"{max_bytes} bytes, "
                f"got {len(data)}"
            )

        length = len(data)

        # --------------------------------------------------
        # LENGTH
        # --------------------------------------------------

        length_bits = format(
            length,
            "08b"
        )

        # --------------------------------------------------
        # CHECKSUM
        # --------------------------------------------------

        checksum_bits = self.checksum(
            data=data,
            length=length,
            checksum_bits=fmt["checksum_bits"],
        )

        # --------------------------------------------------
        # DATA -> BITS
        # --------------------------------------------------

        data_bits = "".join(
            format(byte, "08b")
            for byte in data
        )

        # --------------------------------------------------
        # ZERO PADDING
        # --------------------------------------------------

        padding_length = (
            fmt["data_bits"]
            - len(data_bits)
        )

        data_bits += (
            "0" * padding_length
        )

        # --------------------------------------------------
        # BUILD PAYLOAD
        # --------------------------------------------------

        bits = (
            length_bits
            + checksum_bits
            + data_bits
        )

        expected_bits = (
            plates * self.WORD_BITS
        )

        # --------------------------------------------------
        # Internal consistency check
        # --------------------------------------------------

        if len(bits) != expected_bits:
            raise RuntimeError(
                "Internal format error: "
                f"expected {expected_bits} bits, "
                f"got {len(bits)}"
            )

        # --------------------------------------------------
        # BITS -> WORDS
        # --------------------------------------------------

        mnemonic = []

        for position in range(
            0,
            expected_bits,
            self.WORD_BITS
        ):

            chunk = bits[
                position:
                position + self.WORD_BITS
            ]

            index = self.bits_to_index(
                chunk
            )

            mnemonic.append(
                self.words[index]
            )

        # --------------------------------------------------
        # Final validation
        # --------------------------------------------------

        if len(mnemonic) != plates:
            raise RuntimeError(
                "Internal error: "
                "incorrect mnemonic length"
            )

        return mnemonic

    # ======================================================
    # DECODE
    # ======================================================

    def decode(self, mnemonic):
        """
        Decode exactly 12 or 24 words.
        """

        if not isinstance(mnemonic, (list, tuple)):
            raise TypeError(
                "mnemonic must be a list or tuple"
            )

        if not mnemonic:
            raise ValueError(
                "Empty mnemonic"
            )

        # --------------------------------------------------
        # Exact mnemonic length
        # --------------------------------------------------

        plates = len(mnemonic)

        self.validate_plates(plates)

        fmt = self.FORMAT[plates]

        # --------------------------------------------------
        # WORDS -> BITS
        # --------------------------------------------------

        bits = []

        for position, word in enumerate(
            mnemonic,
            start=1
        ):

            if not isinstance(word, str):
                raise TypeError(
                    f"Word at position {position} "
                    f"must be a string"
                )

            word = word.strip().lower()

            if word not in self.word_to_index:
                raise ValueError(
                    f"Unknown word at position "
                    f"{position}: {word!r}"
                )

            index = self.word_to_index[word]

            bits.append(
                self.index_to_bits(index)
            )

        bits = "".join(bits)

        expected_bits = (
            plates * self.WORD_BITS
        )

        if len(bits) != expected_bits:
            raise RuntimeError(
                "Internal error: "
                "incorrect bit length"
            )

        # --------------------------------------------------
        # READ LENGTH
        # --------------------------------------------------

        offset = 0

        length_bits = bits[
            offset:
            offset + 8
        ]

        offset += 8

        length = int(
            length_bits,
            2
        )

        max_bytes = (
            fmt["data_bits"] // 8
        )

        if length > max_bytes:
            raise ValueError(
                f"Invalid data length: "
                f"{length} bytes for "
                f"{plates} plates"
            )

        # --------------------------------------------------
        # READ CHECKSUM
        # --------------------------------------------------

        checksum_size = fmt[
            "checksum_bits"
        ]

        stored_checksum = bits[
            offset:
            offset + checksum_size
        ]

        offset += checksum_size

        # --------------------------------------------------
        # READ DATA AREA
        # --------------------------------------------------

        data_area_bits = bits[
            offset:
            offset + fmt["data_bits"]
        ]

        if len(data_area_bits) != fmt["data_bits"]:
            raise ValueError(
                "Invalid data area"
            )

        # --------------------------------------------------
        # ACTUAL DATA
        # --------------------------------------------------

        actual_data_bits = data_area_bits[
            :length * 8
        ]

        # --------------------------------------------------
        # ZERO PADDING
        # --------------------------------------------------

        padding_bits = data_area_bits[
            length * 8:
        ]

        if any(
            bit != "0"
            for bit in padding_bits
        ):
            raise ValueError(
                "INVALID PADDING"
            )

        # --------------------------------------------------
        # BITS -> BYTES
        # --------------------------------------------------

        data = bytes(
            int(
                actual_data_bits[i:i + 8],
                2
            )
            for i in range(
                0,
                len(actual_data_bits),
                8
            )
        )

        # --------------------------------------------------
        # CHECKSUM VALIDATION
        # --------------------------------------------------

        expected_checksum = self.checksum(
            data=data,
            length=length,
            checksum_bits=checksum_size,
        )

        if stored_checksum != expected_checksum:
            raise ValueError(
                "INVALID CHECKSUM"
            )

        return data


# ==========================================================
# LOAD REAL WORDLIST
# ==========================================================

with open(
    Path(__file__).resolve().with_name("wordlist4096.txt"),
    "r",
    encoding="utf-8"
) as f:
    words = f.read().splitlines()


r = Recode(words)


# ==========================================================
# CLI
# ==========================================================

def parse_mnemonic_input(raw_text):
    """Normalize a CLI mnemonic string into a list of words."""

    if raw_text is None:
        raise ValueError("No text provided")

    return [
        part.strip().lower()
        for part in raw_text.replace(
            ",",
            " "
        ).split()
        if part.strip()
    ]


def build_parser():
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Encode and decode RECODE mnemonics."
    )

    parser.add_argument(
        "--encode",
        dest="encode_text",
        help="UTF-8 string to encode into mnemonic words",
        metavar="TEXT",
    )

    parser.add_argument(
        "--decode",
        dest="decode_text",
        help="Mnemonic phrase to decode back into a UTF-8 string",
        metavar="TEXT",
    )

    parser.add_argument(
        "--plates",
        type=int,
        choices=(12, 24),
        help="Force 12 or 24 plates when encoding",
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    encode_parser = subparsers.add_parser(
        "encode",
        help="encode a UTF-8 string",
    )
    encode_parser.add_argument(
        "text",
        help="UTF-8 string to encode",
    )
    encode_parser.add_argument(
        "--plates",
        type=int,
        choices=(12, 24),
        help="Force 12 or 24 plates when encoding",
    )

    decode_parser = subparsers.add_parser(
        "decode",
        help="decode a mnemonic phrase",
    )
    decode_parser.add_argument(
        "text",
        help="Mnemonic words separated by spaces",
    )

    return parser


def main(argv=None):
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "encode":
        text = args.text
        plates = args.plates
        mnemonic = r.encode(
            text.encode("utf-8"),
            plates=plates,
        )
        print(" ".join(mnemonic))
        return 0

    if args.command == "decode":
        mnemonic = parse_mnemonic_input(args.text)
        decoded = r.decode(mnemonic).decode("utf-8")
        print(decoded)
        return 0

    if args.encode_text is not None:
        mnemonic = r.encode(
            args.encode_text.encode("utf-8"),
            plates=args.plates,
        )
        print(" ".join(mnemonic))
        return 0

    if args.decode_text is not None:
        mnemonic = parse_mnemonic_input(args.decode_text)
        decoded = r.decode(mnemonic).decode("utf-8")
        print(decoded)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
