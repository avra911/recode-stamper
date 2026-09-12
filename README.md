# Recode Stamper

A small Python utility that encodes UTF-8 text into a 12- or 24-word mnemonic (RECODE) and decodes it back.

## Install from PyPI

```bash
pip install recode-stamper
```

## Quick start

After installation, use the CLI entry point:

```bash
recode --encode "MyPassword123!"
```

```bash
recode --decode "artist scavenge intimate airdrop humdrum curfew hexagon candy comedy bunion brevity aardvark"
```

Subcommands also work:

```bash
recode encode "MyPassword123!"
recode decode "artist scavenge intimate airdrop humdrum curfew hexagon candy comedy bunion brevity aardvark"
```

For interactive use, the CLI can also prompt for text securely without echoing it in the terminal:

```bash
recode --encode
recode encode
```

This is useful for avoiding accidental exposure in shell history or terminal logs.

Show help:

```bash
recode --help
```

If you are running directly from the repository checkout instead of the installed package:

```bash
python recode.py --encode "MyPassword123!"
python recode.py --decode "artist scavenge intimate airdrop humdrum curfew hexagon candy comedy bunion brevity aardvark"
```

## How the format works

The RECODE format uses a fixed 4096-word list.

- Each word is mapped to a 12-bit value
- 2^12 = 4096 unique values
- A word index is therefore a number from 0 to 4095

The format automatically selects between 12 and 24 words:

- up to 16 bytes of data -> 12 words
- 17 to 32 bytes of data -> 24 words
- more than 32 bytes -> rejected

This keeps the output compact while preserving enough space for metadata and a checksum.

You can also force the format explicitly:

```bash
recode --encode "MyPassword123!" --plates 12
recode --encode "MyPassword123!" --plates 24
```

## Why UTF-8

The encoder accepts UTF-8 text and converts it to bytes before packing the bit stream. This means it works for regular ASCII strings as well as non-ASCII text, while preserving deterministic behavior and a fixed wordlist layout.

## Wordlist source

The file `wordlist4096.txt` is based on the public wordlist from:

https://raw.githubusercontent.com/kklash/wordlist4096/main/wordlist4096.txt

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.

The included wordlist is derived from the upstream source referenced above. Please check the original repository and license terms for the wordlist itself before using it in production or redistribution.

This repository does not claim to replace or relicense the upstream wordlist; it only references the source used for the local copy included here.
