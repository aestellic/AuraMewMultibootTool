from data_interface import DataInterface
import os
from itertools import chain
from glob import iglob
import subprocess

def yn_prompt(question: str, default=None) -> bool:
    choices = ("", "y", "n") if default in ("yes", "no") else ("y", "n")
    hint = "Y/n" if default == "yes" else "y/n"
    hint = "y/N" if default == "no" else hint
    reply = None

    while reply not in choices:
        reply = input(f"{question} ({hint}): ").lower()
    return (reply == "y") if default != "yes" else (reply in ("", "y"))

base_rom = os.path.abspath(input("Enter path to base ROM [it's most likely named 'BUUJ - Aura Mew (ENG).gba']: "))
input_folder_path = os.path.abspath(input("Enter path to directory containing patched _mb.gba files [it's most likely named 'mb']: "))
output_folder_path = os.path.abspath(input("Enter path to output directory: "))

reply = yn_prompt("\nThis program will create .bps patches for the compressesd multiboot inside BUUJ - Aura Mew (ENG).gba, based on all multiboots placed in " + input_folder_path + ".\nThe .bps patches will be outputted to " + output_folder_path + ".\nContinue?", default="no")
if not reply:
    exit()

os.makedirs(output_folder_path, exist_ok=True)

print("Working...")

# Base ROM
if not os.path.isfile(base_rom):
    print("Base ROM is not a valid file. Exiting...")
    exit()
else:
    print("Extracting " + os.path.basename(base_rom))
    with open(base_rom, 'rb') as input_file:
        input_file_bytes = input_file.read()
        compressed_data = DataInterface(input_file_bytes)

        if input_file_bytes[0x8B2C:0x8B30] == (0x1094f400).to_bytes(4): # Normal Loader
            mb = bytearray(DataInterface.decompress_read(compressed_data, 0x8B2C).read_all_bytes())
            mb_offset = bytearray(0x10000)
            mb[:0] = mb_offset

            header = [0] * 0xE4
            header[0:0xC0] = input_file_bytes[0:0xC0] # copy header from rom
            
            header[0xC0:0xC4] = (0xea00002f).to_bytes(4, "little") # set entrypoint to 0x02000184
    
            header[0xC4] = 0x2 # Boot mode: normal
            header[0xC5] = 0x1 # Client ID Number
            mb[0:0xE4] = header[0:0xE4]

            filler = [0] * 262144
            mb[len(mb):len(filler)] = filler[len(mb):len(filler)] # checksum will not pass on hardware without this
    
            output_file_path = os.path.abspath(base_rom)[:-4]+"_mb.gba"
            with open(output_file_path, "wb") as output_file:
                output_file.write(mb)
                print("Extracted base multiboot!")
        else:
            print("Base ROM is invalid. Please redump and try again.")
            exit()

# Patched Multiboots
for file in iglob(os.path.join(input_folder_path, "**", "*_mb.gba"), recursive=True):
    relative = os.path.relpath(file, input_folder_path)
    if not os.path.isfile(file):
        continue
    
    print("Creating patch for " + os.path.basename(file))
    output_file_path = os.path.join(output_folder_path, relative[:-4]+".bps")
    print(output_file_path)
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    subprocess.call(['flips', '--create', '--bps-delta', os.path.abspath(base_rom)[:-4]+"_mb.gba", file, output_file_path])
     
os.remove(os.path.abspath(base_rom)[:-4]+"_mb.gba")
print("Done!")