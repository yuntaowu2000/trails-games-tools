# this code is modified from uyjulian unpackpka https://github.com/uyjulian/unpackpka
import sys
import os
import struct

file_path = "E:\\SteamLibrary\\steamapps\\common\\The Legend of Heroes Sen no Kiseki III\\data\\asset\\D3D11\\assets.pka"
path4 = "E:\\games\\The Legend of Heroes Trails of Cold Steel IV\\data\\asset\\D3D11\\assets.pka"
# This script is intended to unpack "pka" file to "pkg" file. (assets.pka from Trails of Cold Steel III/IV PC/Switch)
# syntax: python3 /path/to/unpackpka.py /path/to/assets.pka /path/to/destination/directory
# Destination directory must exist. If it is omitted, it will use current directory instead

def unpack(path, fn=None):
	with open(path, "rb") as f:
		pka_header, = struct.unpack("<I", f.read(4))
		if pka_header != 0x7FF7CF0D:
			raise Exception("This isn't a pka file")
		total_package_entries, = struct.unpack("<I", f.read(4))
		package_entries = {}
		for _ in range(total_package_entries):
			package_name, number_files = struct.unpack("<32sI", f.read(32+4))
			file_entries = []
			for _ in range(number_files):
				file_entry_name, file_entry_hash = struct.unpack("<64s32s", f.read(64+32))
				file_entries.append([file_entry_name.rstrip(b"\x00"), file_entry_hash])
			package_entries[package_name.rstrip(b"\x00").decode("ASCII")] = file_entries
		total_file_entries, = struct.unpack("<I", f.read(4))
		file_entries = {}
		for _ in range(total_file_entries):
			file_entry_hash, file_entry_offset, file_entry_compressed_size, file_entry_uncompressed_size, file_entry_flags = struct.unpack("<32sQIII", f.read(32+8+4+4+4))
			file_entries[file_entry_hash] = [file_entry_offset, file_entry_compressed_size, file_entry_uncompressed_size, file_entry_flags]
		for package_name in package_entries.keys():
			if not package_name in fn:
				continue
			package_file_entries = package_entries[package_name]
			rebased_package_file_entries = {}
			rebased_file_entry_start = 8 + ((64+4+4+4+4) * len(package_file_entries))
			for file_entry in package_file_entries:
				rebased_file_entry = list(file_entries[file_entry[1]]) # clone the list
				rebased_file_entry.append(rebased_file_entry_start) # append the new offset
				rebased_file_entry_start += rebased_file_entry[1]
				rebased_package_file_entries[file_entry[0]] = rebased_file_entry
			with open(package_name, "wb") as wf:
				wf.write(b"\x00\x00\x00\x00")
				wf.write(struct.pack("<I", len(package_file_entries)))
				for file_entry_name in rebased_package_file_entries.keys():
					file_entry = rebased_package_file_entries[file_entry_name]
					wf.write(struct.pack("<64sIIII", file_entry_name, file_entry[2], file_entry[1], file_entry[4], file_entry[3]))
				for file_entry_name in rebased_package_file_entries.keys():
					file_entry = rebased_package_file_entries[file_entry_name]
					f.seek(file_entry[0])
					wf.write(f.read(file_entry[1])) # Copy data

if __name__ == "__main__":
	unpack(path4)