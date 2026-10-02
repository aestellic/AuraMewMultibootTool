# AuraMewMultibootTool

Multiboot extractor + patcher for the Aura Mew Distribution ROM

All patched multiboots have been tested and confirmed to load without a server connection. Distribution has not been thoroughly tested.

## How to Use (for end users)
0) Obtain `BUUJ - Aura Mew (ENG).gba`
1) Install Python 3.14.7
2) Install [Flips](https://git.disroot.org/Sir_Walrus/Flips)
3) Download and extract [the patcher script](https://github.com/aestellic/GEN3PokemonDistributionsMB/archive/refs/heads/main.zip)
4) Open a terminal/command prompt and `cd` to the extracted patcher script folder
5) Run `python3 apply_patch.py` and follow the prompts.

## How to Use (for developers)
0) Obtain `BUUJ - Aura Mew (ENG).gba` or any Aura Mew-based distribution ROM(s).
1) Install Python 3.14.7
2) Install [Flips](https://git.disroot.org/Sir_Walrus/Flips)
3) Clone + `cd` to the repo
4) Run `python3 extract_mb.py` and follow the prompts to extract the multiboot(s).
5) Patch the extracted multiboots as desired.
6) Run `python3 create_patch.py` and follow the prompts to create .bps patches for each patched multiboot based off of the base ROM's multiboot

## License
This project is fully open sourced under the [MIT License](LICENSE).

## Credits
- [LagoLunatic](https://github.com/LagoLunatic/mclib/), for creating an LZ77 extractor
- Goppier, for creating patches for the Aura Mew Distribution ROM which are utilized in this project
> [!NOTE]
> Not linking to Goppier due to them publicly providing patched ROM files
