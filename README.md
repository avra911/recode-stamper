# Recode Stamper

A small Python utility that encodes UTF-8 text into a 12- or 24-word mnemonic (RECODE) and decodes it back.

## How to run

Encode a string:

```bash
python recode.py --encode "MyPassword123!"
```

Decode a mnemonic:

```bash
python recode.py --decode "artist scavenge intimate airdrop humdrum curfew hexagon candy comedy bunion brevity aardvark"
```

Also works with subcommands:

```bash
python recode.py encode "MyPassword123!"
python recode.py decode "artist scavenge intimate airdrop humdrum curfew hexagon candy comedy bunion brevity aardvark"
```

Show help:

```bash
python recode.py --help
```

## Wordlist source

The file `wordlist4096.txt` is based on the public wordlist from:

https://raw.githubusercontent.com/kklash/wordlist4096/main/wordlist4096.txt

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.

The included wordlist is derived from the upstream source referenced above. Please check the original repository and license terms for the wordlist itself before using it in production or redistribution.

This repository does not claim to replace or relicense the upstream wordlist; it only references the source used for the local copy included here.
