from data_interface import DataInterface
import os
from itertools import chain
from glob import iglob

def yn_prompt(question: str, default=None) -> bool:
    choices = ("", "y", "n") if default in ("yes", "no") else ("y", "n")
    hint = "Y/n" if default == "yes" else "y/n"
    hint = "y/N" if default == "no" else hint
    reply = None

    while reply not in choices:
        reply = input(f"{question} ({hint}): ").lower()
    return (reply == "y") if default != "yes" else (reply in ("", "y"))

input_folder_path = os.path.abspath(input("Enter path to folder containing Aura Mew-based Distro ROMs: "))
output_folder_path = os.path.abspath(os.path.join(input_folder_path,"../mb"))

reply = yn_prompt("\nThis program will recusrively extract all Distro ROMs in " + input_folder_path + " to standalone multiboots.\nThese multiboots will be outputted to " + output_folder_path + ".\nContinue?", default="no")
if not reply:
    exit()

os.makedirs(output_folder_path, exist_ok=True)

print("Working...")

for file in iglob(os.path.join(input_folder_path, "**", "*.gba"), recursive=True):
    relative = os.path.relpath(file, input_folder_path)
    if not os.path.isfile(file) or "mb" in relative.split(os.sep):
        continue
    
    print("Extracting " + os.path.basename(file))
    with open(file, 'rb') as input_file:
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

            if mb[0x139c6:0x139ca].hex() == (0x21490888).to_bytes(4).hex(): # PCNY
                mb[0x139c6:0x139ca] = (0xfcf74bff).to_bytes(4) # randomize TID

                # update checksum
                k = 0x0
                j = 0x1c958

                for i in range(0, len(mb[0x1000c:0x1c8f8]),0x4):
                    if i+0x1000c != 0x1c8ec:
                        k += int.from_bytes(mb[i+0x1000c:i+0x1000c+4], "little") & 0xFFFFFFFF
                for j in range(0, len(mb[0x1c958:0x10830+0x10004]),0x4):
                    if j+0x1c958 != 0x1c8ec:
                        k += int.from_bytes(mb[j+0x1c958:j+0x1c958+4], "little") & 0xFFFFFFFF
                
                #print("calculated:" + str(int.from_bytes((k & 0xFFFFFFFF).to_bytes(4, "little"), "little"))) # calculated checksum
                mb[0x10008:0x10008+0x4] = (k & 0xFFFFFFFF).to_bytes(4, "little")
                #print("put:" + str(int.from_bytes(mb[0x10008:0x10008+0x4], "little") & 0xFFFFFFFF)) # checksum that we just placed in the rom
    
            output_file_path = os.path.join(output_folder_path, relative[:-4]+"_mb.gba")
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with open(output_file_path, "wb") as output_file:
                output_file.write(mb)
        else: # TOP10 Loader
            compressed_mb_offsets = [0x8d4c, 0x10a8c, 0x189b4, 0x20888, 0x285cc, 0x302e4, 0x38124, 0x3ff14, 0x47d74, 0x4fbe0]
            for i in range(len(compressed_mb_offsets)):
                mb = bytearray(DataInterface.decompress_read(compressed_data, compressed_mb_offsets[i]).read_all_bytes())
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

                 # could be improved by using a dict instead of a giant switch case, as well as hashing the base rom instead of using hardcoded file names
                match os.path.basename(relative):
                    case "BUUJ - JAA Top 20 -Part 1- (ENG).gba":
                        folder_name = "BUUJ - JAA Top 20 (ENG)"
                        distro_name_part_1 = "BUUJ - JAA Top 20 -"
                        distro_name_part_2 = "- (ENG)_mb.gba"
                        match i:
                            case 0:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"PIKACHU"+distro_name_part_2)
                            case 1:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"CHARIZARD"+distro_name_part_2)
                            case 2:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ZAPDOS"+distro_name_part_2)
                            case 3:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"BULBASAUR"+distro_name_part_2)
                            case 4:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"LATIAS"+distro_name_part_2)
                            case 5:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ARTICUNO"+distro_name_part_2)
                            case 6:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"SUICUNE"+distro_name_part_2)
                            case 7:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ABSOL"+distro_name_part_2)
                            case 8:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ESPEON"+distro_name_part_2)
                            case 9:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"UMBREON"+distro_name_part_2)
                            case _:
                                print("Something has gone very wrong. If you see this, please write an issue!")
                                exit()
                    case "BUUJ - JAA Top 20 -Part 2- (ENG).gba":
                        folder_name = "BUUJ - JAA Top 20 (ENG)"
                        distro_name_part_1 = "BUUJ - JAA Top 20 -"
                        distro_name_part_2 = "- (ENG)_mb.gba"
                        match i:
                            case 0:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"BLASTOISE"+distro_name_part_2)
                            case 1:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"LATIOS"+distro_name_part_2)
                            case 2:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"MOLTRES"+distro_name_part_2)
                            case 3:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ALAKAZAM"+distro_name_part_2)
                            case 4:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ENTEI"+distro_name_part_2)
                            case 5:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"TYPHLOSION"+distro_name_part_2)
                            case 6:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"RAIKOU"+distro_name_part_2)
                            case 7:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"TYRANITAR"+distro_name_part_2)
                            case 8:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"BLAZIKEN"+distro_name_part_2)
                            case 9:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"DRAGONITE"+distro_name_part_2)
                            case _:
                                print("Something has gone very wrong. If you see this, please write an issue!")
                                exit()
                    case "BUUJ - POTD Top 20 -Part 1- (ENG).gba":
                        folder_name = "BUUJ - POTD Top 20 (ENG)"
                        distro_name_part_1 = "BUUJ - POTD Top 20 -"
                        distro_name_part_2 = "- (ENG)_mb.gba"
                        match i:
                            case 0:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"PIKACHU"+distro_name_part_2)
                            case 1:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"CHARIZARD"+distro_name_part_2)
                            case 2:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ZAPDOS"+distro_name_part_2)
                            case 3:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"BULBASAUR"+distro_name_part_2)
                            case 4:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"LATIAS"+distro_name_part_2)
                            case 5:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ARTICUNO"+distro_name_part_2)
                            case 6:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"SUICUNE"+distro_name_part_2)
                            case 7:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ABSOL"+distro_name_part_2)
                            case 8:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ESPEON"+distro_name_part_2)
                            case 9:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"UMBREON"+distro_name_part_2)
                            case _:
                                print("Something has gone very wrong. If you see this, please write an issue!")
                                exit()
                    case "BUUJ - POTD Top 20 -Part 2- (ENG).gba":
                        folder_name = "BUUJ - POTD Top 20 (ENG)"
                        distro_name_part_1 = "BUUJ - POTD Top 20 -"
                        distro_name_part_2 = "- (ENG)_mb.gba"
                        match i:
                            case 0:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"BLASTOISE"+distro_name_part_2)
                            case 1:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"LATIOS"+distro_name_part_2)
                            case 2:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"MOLTRES"+distro_name_part_2)
                            case 3:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ALAKAZAM"+distro_name_part_2)
                            case 4:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"ENTEI"+distro_name_part_2)
                            case 5:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"TYPHLOSION"+distro_name_part_2)
                            case 6:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"RAIKOU"+distro_name_part_2)
                            case 7:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"TYRANITAR"+distro_name_part_2)
                            case 8:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"BLAZIKEN"+distro_name_part_2)
                            case 9:
                                output_file_path = os.path.join(output_folder_path, os.path.dirname(relative), folder_name, distro_name_part_1+"DRAGONITE"+distro_name_part_2)
                            case _:
                                print("Something has gone very wrong. If you see this, please write an issue!")
                                exit()
                    case _:
                        print("Unknown TOP10 loader ROM encountered. ("+relative+"). Using placeholder output file names.")
                        output_file_path = os.path.join(output_folder_path, str(i)+"_", relative[:-4]+"_mb.gba")
                    
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                with open(output_file_path, "wb") as output_file:
                    output_file.write(mb)

print("Done!")