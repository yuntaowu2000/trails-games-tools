# ED9 / Kuro no Kiseki mdl format reversing.
# Modified from https://gist.github.com/uyjulian/9a9d6395682dac55d113b503b1172009
# Useful only when used with parseKuroModel.py for map files.
# For character files, need to wait for a better image integration

import sys
import io
import struct


import array
import pprint
import os

import math

## Model reading code at 7FF76D082B90 in ED9 pc

def arr_rad_to_quat(a):
	if len(a) < 4:
		a.append(0.0)
	cy = math.cos(a[2] * 0.5)
	sy = math.sin(a[2] * 0.5)
	cp = math.cos(a[1] * 0.5)
	sp = math.sin(a[1] * 0.5)
	cr = math.cos(a[0] * 0.5)
	sr = math.sin(a[0] * 0.5)
	a[0] = sr * cp * cy - cr * sp * sy # X
	a[1] = cr * sp * cy + sr * cp * sy # Y
	a[2] = cr * cp * sy - sr * sp * cy # Z
	a[3] = cr * cp * cy + sr * sp * sy # W

def cast_memoryview(mv, t):
	return mv.cast(t)

def multiply_array_as_4x4_matrix(arra, arrb):
	newarr = cast_memoryview(memoryview(bytearray(cast_memoryview(memoryview(arra), "B"))), "f")
	for i in range(4):
		for j in range(4):
			newarr[(i * 4) + j] = 0 + (arrb[(i * 4) + 0] * arra[j +  0]) + (arrb[(i * 4) + 1] * arra[j +  4]) + (arrb[(i * 4) + 2] * arra[j +  8]) + (arrb[(i * 4) + 3] * arra[j + 12])
	return newarr

def invert_matrix_44(m):
	inv = cast_memoryview(memoryview(bytearray(cast_memoryview(memoryview(m), "B"))), "f")

	inv[0] = m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] + m[9] * m[7] * m[14] +m[13] * m[6] * m[11] - m[13] * m[7] * m[10]
	inv[1] = -m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] - m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10]
	inv[2] = m[1] * m[6] * m[15] - m[1] * m[7] * m[14] - m[5] * m[2] * m[15] + m[5] * m[3] * m[14] + m[13] * m[2] * m[7] - m[13] * m[3] * m[6]
	inv[3] = -m[1] * m[6] * m[11] + m[1] * m[7] * m[10] + m[5] * m[2] * m[11] - m[5] * m[3] * m[10] - m[9] * m[2] * m[7] + m[9] * m[3] * m[6]
	inv[4] = -m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] - m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10]
	inv[5] = m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] + m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10]
	inv[6] = -m[0] * m[6] * m[15] + m[0] * m[7] * m[14] + m[4] * m[2] * m[15] - m[4] * m[3] * m[14] - m[12] * m[2] * m[7] + m[12] * m[3] * m[6]
	inv[7] = m[0] * m[6] * m[11] - m[0] * m[7] * m[10] - m[4] * m[2] * m[11] + m[4] * m[3] * m[10] + m[8] * m[2] * m[7] - m[8] * m[3] * m[6]
	inv[8] = m[4] * m[9] * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] + m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9]
	inv[9] = -m[0] * m[9] * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] - m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9]
	inv[10] = m[0] * m[5] * m[15] - m[0] * m[7] * m[13] - m[4] * m[1] * m[15] + m[4] * m[3] * m[13] + m[12] * m[1] * m[7] - m[12] * m[3] * m[5]
	inv[11] = -m[0] * m[5] * m[11] + m[0] * m[7] * m[9] + m[4] * m[1] * m[11] - m[4] * m[3] * m[9] - m[8] * m[1] * m[7] + m[8] * m[3] * m[5]
	inv[12] = -m[4] * m[9] * m[14] + m[4] * m[10] * m[13] +m[8] * m[5] * m[14] - m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9]
	inv[13] = m[0] * m[9] * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] + m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9]
	inv[14] = -m[0] * m[5] * m[14] + m[0] * m[6] * m[13] + m[4] * m[1] * m[14] - m[4] * m[2] * m[13] - m[12] * m[1] * m[6] + m[12] * m[2] * m[5]
	inv[15] = m[0] * m[5] * m[10] - m[0] * m[6] * m[9] - m[4] * m[1] * m[10] + m[4] * m[2] * m[9] + m[8] * m[1] * m[6] - m[8] * m[2] * m[5]

	det = m[0] * inv[0] + m[1] * inv[4] + m[2] * inv[8] + m[3] * inv[12]
	if (det == 0):
		return None

	det = 1.0 / det
	for i in range(16):
		inv[i] *= det

	return inv

# based on https://github.com/donmccurdy/glTF-Transform/blob/0ffa610a82594df3394b3f0aed4d2cb7dce5d2bf/packages/core/src/utils/math-utils.ts#L121
def compose_matrix_44(mat, translation, rotation, scale):
	te = mat

	x = rotation[0]
	y = rotation[1]
	z = rotation[2]
	w = rotation[3]

	x2 = x + x
	y2 = y + y
	z2 = z + z
	xx = x * x2
	xy = x * y2
	xz = x * z2
	yy = y * y2
	yz = y * z2
	zz = z * z2
	wx = w * x2
	wy = w * y2
	wz = w * z2

	sx = scale[0]
	sy = scale[1]
	sz = scale[2]

	te[0] = (1.0 - (yy + zz)) * sx
	te[1] = (xy + wz) * sx
	te[2] = (xz - wy) * sx
	te[3] = 0.0

	te[4] = (xy - wz) * sy
	te[5] = (1.0 - (xx + zz)) * sy
	te[6] = (yz + wx) * sy
	te[7] = 0.0

	te[8] = (xz + wy) * sz
	te[9] = (yz - wx) * sz
	te[10] = (1.0 - (xx + yy)) * sz
	te[11] = 0.0

	te[12] = translation[0]
	te[13] = translation[1]
	te[14] = translation[2]
	te[15] = 1.0

ed9_asset_config_shader_info = {
	"chr_cloth" : {
		0 : "SWITCH_DIFFUSEMAP0",
		1 : "SWITCH_DIFFUSEMAP1",
		2 : "SWITCH_DIFFUSEMAP2",
		3 : "SWITCH_NORMALMAP0",
		4 : "SWITCH_NORMALMAP1",
		5 : "SWITCH_GLOWMAP0",
		6 : "SWITCH_GLOWMAP1",
		7 : "SWITCH_MASKMAP0",
		8 : "SWITCH_MASKMAP1",
		9 : "SWITCH_TOONMAP",
	},
	"chr_eye" : {
		0 : "SWITCH_DIFFUSEMAP0",
		1 : "SWITCH_DIFFUSEMAP1",
		2 : "SWITCH_DIFFUSEMAP2",
		5 : "SWITCH_GLOWMAP0",
		6 : "SWITCH_GLOWMAP1",
		7 : "SWITCH_MASKMAP0",
		8 : "SWITCH_MASKMAP1",
		9 : "SWITCH_TOONMAP",
	},
	"chr_hair" : {
		0 : "SWITCH_DIFFUSEMAP0",
		1 : "SWITCH_DIFFUSEMAP1",
		2 : "SWITCH_DIFFUSEMAP2",
		3 : "SWITCH_NORMALMAP0",
		4 : "SWITCH_NORMALMAP1",
		5 : "SWITCH_GLOWMAP0",
		6 : "SWITCH_GLOWMAP1",
		7 : "SWITCH_MASKMAP0",
		8 : "SWITCH_MASKMAP1",
		9 : "SWITCH_TOONMAP",
	},
	"chr_skin" : {
		0 : "SWITCH_DIFFUSEMAP0",
		1 : "SWITCH_DIFFUSEMAP1",
		2 : "SWITCH_DIFFUSEMAP2",
		3 : "SWITCH_NORMALMAP0",
		4 : "SWITCH_NORMALMAP1",
		5 : "SWITCH_GLOWMAP0",
		6 : "SWITCH_GLOWMAP1",
		7 : "SWITCH_MASKMAP0",
		8 : "SWITCH_MASKMAP1",
		9 : "SWITCH_TOONMAP",
	},
	"map" : {
		0 : "SWITCH_DIFFUSEMAP0",
		1 : "SWITCH_DIFFUSEMAP1",
		2 : "SWITCH_DIFFUSEMAP2",
		3 : "SWITCH_NORMALMAP0",
		4 : "SWITCH_NORMALMAP1",
		5 : "SWITCH_NORMALMAP2",
		6 : "SWITCH_MASKMAP0",
		7 : "SWITCH_MASKMAP1",
		8 : "SWITCH_MASKMAP2",
		9 : "SWITCH_TOONMAP",
		1 : "SWITCH_DUDVMAP0",
	},
	"water" : {
		0 : "SWITCH_DIFFUSEMAP0",
		1 : "SWITCH_DIFFUSEMAP1",
		4 : "SWITCH_DIFFUSEMAP2",
		2 : "SWITCH_GLOWMAP0",
		3 : "SWITCH_GLOWMAP1",
	},
	"monster" : {
		0 : "SWITCH_DIFFUSEMAP0",
		1 : "SWITCH_DIFFUSEMAP1",
		2 : "SWITCH_DIFFUSEMAP2",
		3 : "SWITCH_NORMALMAP0",
		4 : "SWITCH_NORMALMAP1",
		5 : "SWITCH_MASKMAP0",
		6 : "SWITCH_MASKMAP1",
		7 : "SWITCH_TOONMAP",
		8 : "SWITCH_DUDVMAP",
		9 : "TRANSLUCENT_MAP",
	},
	"fur" : {
		0 : "SWITCH_DIFFUSEMAP0",
		2 : "SWITCH_NORMALMAP0",
		4 : "",
		5 : "SWITCH_TOONMAP",
	},
	"minimap" : {
		0 : "SWITCH_DIFFUSEMAP0",
	},
}

def read_mdl_to_gltf(infn):
	gltf_data = {}
	asset = {}
	asset["generator"] = "ed9mdl2gltf"
	asset["version"] = "2.0"
	gltf_data["asset"] = asset
	buffers = []
	# We'll modify this later
	buffer0 = {}
	buffers.append(buffer0)
	gltf_data["buffers"] = buffers
	bufferviews = []
	gltf_data["bufferViews"] = bufferviews
	accessors = []
	gltf_data["accessors"] = accessors
	embedded_giant_buffer = []
	embedded_giant_buffer_length = [0]
	meshes = []
	gltf_data["meshes"] = meshes
	skins_unprocessed = []
	skins = []
	gltf_data["skins"] = skins
	images = []
	gltf_data["images"] = images
	samplers = []
	gltf_data["samplers"] = samplers
	textures = []
	gltf_data["textures"] = textures
	materials = []
	gltf_data["materials"] = materials
	nodes = []
	gltf_data["nodes"] = nodes
	animations = []
	gltf_data["animations"] = animations
	gltf_data["scene"] = 0
	scenes = []
	if True:
		scene = {}
		scene["nodes"] = [0]
		scenes.append(scene)
	gltf_data["scenes"] = scenes

	mdl_version = []

	primitive_shiz = []

	all_images = set()

	def append_vertex_data(data_bytes, data_count=0, component_type=5126, value_type="VEC3"):
		accessor = {}
		accessor["bufferView"] = len(bufferviews)
		accessor["componentType"] = component_type
		accessor["type"] = value_type
		accessor["count"] = data_count
		accessor_id = len(accessors)
		bufferview = {}
		if True:
			blobdata = data_bytes

			bufferview["buffer"] = 0
			bufferview["byteOffset"] = embedded_giant_buffer_length[0]
			bufferview["byteLength"] = len(blobdata)
			embedded_giant_buffer.append(blobdata)
			embedded_giant_buffer_length[0] += len(blobdata)
			padding_length = (4 - (len(blobdata) % 4))
			embedded_giant_buffer.append(b"\x00" * padding_length)
			embedded_giant_buffer_length[0] += padding_length
		bufferviews.append(bufferview)
		accessors.append(accessor)
		return accessor_id

	def data_reduce_int_to_short(data_bytes):
		data_bytes_mv = memoryview(data_bytes).cast("I")
		data_bytes_mv2 = memoryview(bytearray(len(data_bytes_mv) * 2)).cast("H")
		for i in range(len(data_bytes_mv)):
			data_bytes_mv2[i] = data_bytes_mv[i]
		return bytes(data_bytes_mv2)

	def read_pascal_string(f):
		sz = int.from_bytes(f.read(1), byteorder="little")
		return f.read(sz)

	jointshiz = []
	def read_vertex_data(f, mesh_index, submesh_index, vertex_dump):
		material_offset = int.from_bytes(f.read(4), byteorder="little") # material offset ?
		num_of_elements = 0
		primitive_data_for_vertex = []
		if mdl_version[0] != 1:
			primitive_data_for_vertex = [x for x in primitive_shiz if x["mesh"] == mesh_index and x["submesh"] == submesh_index]
		if mdl_version[0] == 1:
			num_of_elements = int.from_bytes(f.read(4), byteorder="little") # total amount of chunks
		else:
			num_of_elements = len(primitive_data_for_vertex)
			triangle_count = int.from_bytes(f.read(4), byteorder="little")
			f.read(4) # unk

		primitive = {}
		attributes = {}
		primitive["attributes"] = attributes
		primitive["material"] = material_offset
		texcoord_count = 0
		weight_count = 0
		joint_count = 0
		color_count = 0
		ibm_count = 0
		for i in range(num_of_elements):
			primitive_obj = None
			if mdl_version[0] != 1:
				primitive_obj = primitive_data_for_vertex[i]
			# type of chunk
			type_int = 0
			if mdl_version[0] == 1:
				type_int = int.from_bytes(f.read(4), byteorder="little")
			else:
				type_int = primitive_obj["type_int"]
			# total size of chunk
			size_int = 0
			if mdl_version[0] == 1:
				size_int = int.from_bytes(f.read(4), byteorder="little")
			else:
				size_int = primitive_obj["size_int"]
			# stride to next set of elements
			stride_int = 0
			if mdl_version[0] == 1:
				stride_int = int.from_bytes(f.read(4), byteorder="little")
			else:
				stride_int = primitive_obj["stride_int"]
			# print(type_int, size_int, stride_int)
			data_pos = f.tell()
			data = b""
			if mdl_version[0] == 1:
				data = f.read(size_int)
			else:
				data = primitive_obj["data_bytes"]
			if type_int == 0: # Position (12 bytes) (Validated using RenderDoc)
				if stride_int != 12:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 0")
					n = list(memoryview(data).cast("f"))
					for i in range(0, len(n), 3):
						print("%f %f %f" % (n[i + 0], n[i + 1], n[i + 2]))
				if "POSITION" in attributes:
					raise Exception("Position already in attributes")
				attributes["POSITION"] = append_vertex_data(data, size_int // stride_int, 5126, "VEC3")
			elif type_int == 1: # Normal (12 bytes) (Validated using RenderDoc)
				if stride_int != 12:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 1")
					n = list(memoryview(data).cast("f"))
					for i in range(0, len(n), 3):
						print("%f %f %f" % (n[i + 0], n[i + 1], n[i + 2]))
				attributes["NORMAL"] = append_vertex_data(data, size_int // stride_int, 5126, "VEC3")
			elif type_int == 2: # Tangent (12 bytes) (Validated using RenderDoc)
				if stride_int != 12:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 2")
					n = list(memoryview(data).cast("f"))
					for i in range(0, len(n), 3):
						print("%f %f %f" % (n[i + 0], n[i + 1], n[i + 2]))
				attributes["TANGENT"] = append_vertex_data(data, size_int // stride_int, 5126, "VEC3")
			elif type_int == 3: # ??? (16 bytes, split into 2 chunks, or 4 bytes split into 2 chunks)
				if stride_int != 16 and stride_int != 4:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 3")
					if stride_int == 16:
						n = list(memoryview(data).cast("f"))
						for i in range(0, len(n), 4):
							print("%f %f %f %f" % (n[i + 0], n[i + 1], n[i + 2], n[i + 3]))
					elif stride_int == 4:
						n = list(memoryview(data).cast("I"))
						for i in range(0, len(n), 1):
							print("%d" % (n[i + 0]))
				# attributes["COLOR_" + str(color_count)] = append_vertex_data(data, size_int // stride_int, 5126, "VEC4")
				# color_count += 1
				# mv = memoryview(data).cast("f")
				ibm_count += 1
			elif type_int == 4: # Texcoord (8 bytes) (Validated using RenderDoc)
				if stride_int != 8:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 4")
					n = list(memoryview(data).cast("f"))
					for i in range(0, len(n), 2):
						print("%f %f" % (n[i + 0], n[i + 1]))
				texcoords_modded = array.array("f", data)
				attributes["TEXCOORD_" + str(texcoord_count)] = append_vertex_data(bytes(texcoords_modded), size_int // stride_int, 5126, "VEC2")
				texcoord_count += 1
			elif type_int == 5: # Blend weights (16 bytes) (Validated using RenderDoc)
				if stride_int != 16:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 5")
					n = list(memoryview(data).cast("f"))
					for i in range(0, len(n), 4):
						print("%f %f %f %f" % (n[i + 0], n[i + 1], n[i + 2], n[i + 3]))
				weights_clamped = array.array("f", data)
				for i in range(len(weights_clamped)):
					cl = weights_clamped[i]
					if cl > 1.0:
						cl = 1.0
					if cl < 0.0:
						cl = 0.0
					weights_clamped[i] = cl
				attributes["WEIGHTS_" + str(weight_count)] = append_vertex_data(bytes(weights_clamped), size_int // stride_int, 5126, "VEC4")
				weight_count += 1
			elif type_int == 6: # joints (16 bytes)
				if stride_int != 16:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 6")
					n = list(memoryview(data).cast("f"))
					for i in range(0, len(n), 4):
						print("%f %f %f %f" % (n[i + 0], n[i + 1], n[i + 2], n[i + 3]))
				bax = memoryview(bytearray(data_reduce_int_to_short(data))).cast("H")
				for i in range(len(bax)):
					bax[i] += 0
				attributes["JOINTS_" + str(joint_count)] = append_vertex_data(bytes(bax), size_int // stride_int, 5123, "VEC4")
				joint_count += 1
			elif type_int == 7: # Indexes (4 bytes) (Validated using RenderDoc)
				if stride_int != 4:
					raise Exception("Unhandled stride " + str(stride_int))
				if vertex_dump:
					print("TYPE INT 7")
					n = list(memoryview(data).cast("I"))
					for i in range(0, len(n), 1):
						print("%d" % (n[i + 0]))
				primitive["indices"] = append_vertex_data(data, size_int // stride_int, 5125, "SCALAR")
				primitive["mode"] = 4 # TRIANGLES
			else:
				raise Exception("Unknown vertex data type " + str(type_int))
		return primitive
			
	def read_section_2(dat):
		f = io.BytesIO(dat)
		n = ("X")
		n = (struct.unpack('f', f.read(4))[0]) # unk float
		n = (struct.unpack('f', f.read(4))[0]) # unk float
		n = (struct.unpack('f', f.read(4))[0]) # unk float
		n = (struct.unpack('I', f.read(4))[0]) # unk int
		n = (struct.unpack('f', f.read(4))[0]) # unk float
		n = (struct.unpack('f', f.read(4))[0]) # unk float
		n = (struct.unpack('f', f.read(4))[0]) # unk float
		n = (int.from_bytes(f.read(4), byteorder="little")) # unk 0
		n = (int.from_bytes(f.read(4), byteorder="little")) # unk 0
		n = (int.from_bytes(f.read(4), byteorder="little")) # unk 0
		n = (int.from_bytes(f.read(4), byteorder="little")) # unk 0

	def read_mesh_data(dat):
		f = io.BytesIO(dat)
		num_of_elements = int.from_bytes(f.read(4), byteorder="little") # number of elements (5)
		for i in range(num_of_elements):
			vertex_dump = False
			name = read_pascal_string(f)
			name = name.decode("ASCII")
			total_size_of_section = int.from_bytes(f.read(4), byteorder="little") # Total size of section: 1856
			section_data = f.read(total_size_of_section)
			f_section_data = io.BytesIO(section_data)
			primitive_count = int.from_bytes(f_section_data.read(4), byteorder="little")
			mesh = {}
			mesh["name"] = name
			mesh["primitives"] = []
			for ii in range(primitive_count):
				mesh["primitives"].append(read_vertex_data(f_section_data, i, ii, vertex_dump))
			node_count = int.from_bytes(f_section_data.read(4), byteorder="little")
			if node_count > 0:
				skin_unprocessed = {}
				skin_unprocessed["mesh_id"] = len(meshes)
				ibm_str_arr = []
				ibm_data_arr = []
				for i in range(node_count):
					bone_target_name = read_pascal_string(f_section_data).decode("ASCII")
					ibm_str_arr.append(bone_target_name)
					ent = f_section_data.read(4 * 16)
					ibm_data_arr.append(ent)
				skin_unprocessed["names"] = ibm_str_arr
				skin_unprocessed["matrices"] = ibm_data_arr
				skins_unprocessed.append(skin_unprocessed)
			total_size_of_section_2 = int.from_bytes(f.read(4), byteorder="little")
			section_data_2 = f.read(total_size_of_section_2)
			read_section_2(section_data_2)

			meshes.append(mesh)
		# print("Mesh data total: ", f.tell(), len(dat))

	def read_hierarchy_data(dat):
		f = io.BytesIO(dat)
		num_of_elements = int.from_bytes(f.read(4), byteorder="little") # number of elements (5)
		for i in range(num_of_elements):
			node = {}
			name = read_pascal_string(f)
			name = name.decode("ASCII")
			node["name"] = name

			type_int = int.from_bytes(f.read(4), byteorder="little") # unk 0
			mesh_index = int.from_bytes(f.read(4), byteorder="little") # unk 0xffffffff (mapping to mesh index for type 2?)
			if type_int == 0: # transform only
				pass
			elif type_int == 1: # skin child
				pass
			elif type_int == 2: # mesh
				if mesh_index != 0xffffffff:
					node["mesh"] = mesh_index
			position_1 = struct.unpack('f', f.read(4))[0] # unk 0
			position_2 = struct.unpack('f', f.read(4))[0] # unk 0
			position_3 = struct.unpack('f', f.read(4))[0] # unk 0
			unk_2_1 = struct.unpack('f', f.read(4))[0] # unk 0 (rotation?)
			unk_2_2 = struct.unpack('f', f.read(4))[0] # unk 0 (rotation?)
			unk_2_3 = struct.unpack('f', f.read(4))[0] # unk 0 (rotation?)
			unk_2_4 = struct.unpack('f', f.read(4))[0] # unk float 1 (rotation)
			
			skin_mesh = int.from_bytes(f.read(4), byteorder="little") # unk 0 (skin mesh?)
			rotation_2_1 = struct.unpack('f', f.read(4))[0] # unk 0 (rotation in radians type_int==1?)
			rotation_2_2 = struct.unpack('f', f.read(4))[0] # unk 0 (rotation in radians type_int==1?)
			rotation_2_3 = struct.unpack('f', f.read(4))[0] # unk 0 (rotation in radians type_int==1?)
			node_rotation = [rotation_2_1, rotation_2_2, rotation_2_3]
			arr_rad_to_quat(node_rotation)
			# NOTE: the rotation is known to be incorrect.
			# The bone matrices as read in the mesh data portion has correct rotations.
			scale_1 = struct.unpack('f', f.read(4))[0] # unk float 1 (scale?)
			scale_2 = struct.unpack('f', f.read(4))[0] # unk float 1 (scale?)
			scale_3 = struct.unpack('f', f.read(4))[0] # unk float 1 (scale?)
			node_scale = [scale_1, scale_2, scale_3]
			unk_3_1 = struct.unpack('f', f.read(4))[0] # unk 0 (position?)
			unk_3_2 = struct.unpack('f', f.read(4))[0] # unk 0 (position?)
			unk_3_3 = struct.unpack('f', f.read(4))[0] # unk 0 (position?)

			node_translation = [position_1, position_2, position_3]

			node["translation"] = node_translation
			node["rotation"] = node_rotation
			node["scale"] = node_scale

			children = []
			num_of_children = int.from_bytes(f.read(4), byteorder="little") # children count

			for ii in range(num_of_children):
				children.append(int.from_bytes(f.read(4), byteorder="little")) # children index
			if len(children) > 0:
				node["children"] = children
			nodes.append(node)
		# print("Hierachy data total: ", f.tell(), len(dat))

	def read_material_data(dat):
		f = io.BytesIO(dat)
		num_of_elements = int.from_bytes(f.read(4), byteorder="little") # number of elements (2)
		matinfo_all = []
		for i in range(num_of_elements):
			matinfo = {}
			material_name1 = read_pascal_string(f)
			shader_name = read_pascal_string(f)
			str3 = read_pascal_string(f)
			shader_name_ascii = shader_name.decode("ASCII")
			matinfo["material_name1"] = material_name1.decode("ASCII")
			matinfo["shader_name"] = shader_name_ascii
			matinfo["str3"] = str3.decode("ASCII")
			shader_info = {}
			if shader_name_ascii in ed9_asset_config_shader_info:
				shader_info = ed9_asset_config_shader_info[shader_name_ascii]
			num_of_elements_textures = int.from_bytes(f.read(4), byteorder="little")
			switch_to_texture_id = {}
			texinfo_all = []
			matinfo["texinfo_all"] = texinfo_all
			for ii in range(num_of_elements_textures):
				texinfo = {}
				texture_name = read_pascal_string(f)
				texinfo["texture_name"] = texture_name.decode("ASCII")
				texture_slot = int.from_bytes(f.read(4), byteorder="little")
				texinfo["texture_slot"] = texture_slot
				if mdl_version[0] != 1:
					unk_00 = int.from_bytes(f.read(4), byteorder="little")
					texinfo["unk_00"] = unk_00
				texture_wrap_u = int.from_bytes(f.read(4), byteorder="little")
				texinfo["texture_wrap_u"] = texture_wrap_u
				texture_wrap_v = int.from_bytes(f.read(4), byteorder="little")
				texinfo["texture_wrap_v"] = texture_wrap_v
				if mdl_version[0] != 1:
					unk_03 = int.from_bytes(f.read(4), byteorder="little")
					texinfo["unk_03"] = unk_03
				image_name = texture_name.decode("ASCII")
				image = {}
				if True:
					image["uri"] = image_name + ".png"
					all_images.add(image_name)
				image_id = len(images)
				images.append(image)
				sampler = {}
				texture_wrap_map = {
					0 : 10497, # REPEAT
					1 : 33648, # MIRRORED_REPEAT
					2 : 33071, # CLAMP_TO_EDGE
				}
				texture_wrap_u_gltf = 10497
				if texture_wrap_u in texture_wrap_map:
					texture_wrap_u_gltf = texture_wrap_map[texture_wrap_u]
				sampler["wrapS"] = texture_wrap_u_gltf # MIRROR
				texture_wrap_v_gltf = 10497
				if texture_wrap_v in texture_wrap_map:
					texture_wrap_v_gltf = texture_wrap_map[texture_wrap_v]
				sampler["wrapT"] = texture_wrap_v_gltf # MIRROR
				sampler_id = len(samplers)
				samplers.append(sampler)
				texture = {}
				texture["source"] = image_id
				texture["sampler"] = sampler_id
				texture_id = len(textures)
				textures.append(texture)
				# print(material_name1, shader_info[texture_slot], image_name)
				# print(image_name)
				if texture_slot in shader_info:
					texinfo["texture_switch"] = shader_info[texture_slot]
					switch_to_texture_id[shader_info[texture_slot]] = texture_id
				texinfo_all.append(texinfo)
			shaderparaminfo_all = []
			matinfo["shaderparaminfo_all"] = shaderparaminfo_all
			num_of_elements_shaderparam = int.from_bytes(f.read(4), byteorder="little") # number of elements (2)
			for ii in range(num_of_elements_shaderparam):
				shaderparaminfo = {}
				shaderparam_name = read_pascal_string(f)
				shaderparaminfo["shaderparam_name"] = shaderparam_name.decode("ASCII")
				shaderparam_data = []
				shaderparaminfo["shaderparam_data"] = shaderparam_data
				type_int = int.from_bytes(f.read(4), byteorder="little")
				shaderparaminfo["type_int"] = type_int
				if type_int in [0, 1]:
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
				elif type_int in [2]:
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
				elif type_int in [3]:
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
				elif type_int in [4]:
					shaderparam_data.append(struct.unpack('f', f.read(4))[0])
				elif type_int in [5]:
					shaderparam_data.append(struct.unpack('f', f.read(4))[0])
					shaderparam_data.append(struct.unpack('f', f.read(4))[0])
				elif type_int in [6]:
					shaderparam_data.append(struct.unpack('f', f.read(4))[0])
					shaderparam_data.append(struct.unpack('f', f.read(4))[0])
					shaderparam_data.append(struct.unpack('f', f.read(4))[0])
				elif type_int in [7]:
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
				elif type_int in [8]:
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))
					shaderparam_data.append(int.from_bytes(f.read(4), byteorder="little"))

				elif type_int == 0xFFFFFFFF:
					continue
				else:
					raise Exception("Unknown material type " + str(type_int))
				shaderparaminfo_all.append(shaderparaminfo)
			material_switches_count = int.from_bytes(f.read(4), byteorder="little")
			material_switches = {}
			for ii in range(material_switches_count):
				material_switch_str = read_pascal_string(f)
				int2 = int.from_bytes(f.read(4), byteorder="little")
				material_switches[material_switch_str.decode("ASCII")] = int2
			matinfo["material_switches"] = material_switches

			uv_map_index_count = (struct.unpack('I', f.read(4))[0])
			uv_map_indices = []
			matinfo["uv_map_indices"] = uv_map_indices
			for ii in range(uv_map_index_count):
				uv_map_index = (struct.unpack('B', f.read(1))[0])
				uv_map_indices.append(uv_map_index)
			unkX_count = (struct.unpack('I', f.read(4))[0])
			unkX_data = []
			matinfo["unkX_data"] = unkX_data
			for ii in range(unkX_count):
				unkX_x = (struct.unpack('B', f.read(1))[0])
				unkX_data.append(unkX_x)
			n = (struct.unpack('I', f.read(4))[0]) # unk int
			matinfo["unk_int1"] = n
			n = (struct.unpack('I', f.read(4))[0]) # unk int
			matinfo["unk_int2"] = n
			n = (struct.unpack('I', f.read(4))[0]) # unk int
			matinfo["unk_int3"] = n
			n = (struct.unpack('f', f.read(4))[0]) # unk int
			matinfo["unk_int4"] = n
			n = (struct.unpack('I', f.read(4))[0]) # unk int
			matinfo["unk_int5"] = n
			material = {}
			material["name"] = material_name1.decode("ASCII")
			# TODO: UV index
			if "SWITCH_DIFFUSEMAP0" in switch_to_texture_id:
				textureInfo = {}
				textureInfo["index"] = switch_to_texture_id["SWITCH_DIFFUSEMAP0"]
				textureInfo_extensions = {}
				textureInfo_extensions_KHR_texture_transform = {}
				textureInfo_extensions_KHR_texture_transform["offset"] = [0, 0]
				textureInfo_extensions_KHR_texture_transform["rotation"] = 0
				textureInfo_extensions_KHR_texture_transform["scale"] = [1, -1]
				textureInfo_extensions["KHR_texture_transform"] = textureInfo_extensions_KHR_texture_transform
				textureInfo["extensions"] = textureInfo_extensions
				pbrMetallicRoughness = {}
				pbrMetallicRoughness["baseColorTexture"] = textureInfo
				pbrMetallicRoughness["metallicFactor"] = 0.0
				material["pbrMetallicRoughness"] = pbrMetallicRoughness
			if "SWITCH_NORMALMAP0" in switch_to_texture_id:
				textureInfo = {}
				textureInfo["index"] = switch_to_texture_id["SWITCH_NORMALMAP0"]
				textureInfo_extensions = {}
				textureInfo_extensions_KHR_texture_transform = {}
				textureInfo_extensions_KHR_texture_transform["offset"] = [0, 0]
				textureInfo_extensions_KHR_texture_transform["rotation"] = 0
				textureInfo_extensions_KHR_texture_transform["scale"] = [1, -1]
				textureInfo_extensions["KHR_texture_transform"] = textureInfo_extensions_KHR_texture_transform
				textureInfo["extensions"] = textureInfo_extensions
				material["normalTexture"] = textureInfo
			materials.append(material)
			matinfo_all.append(matinfo)

		if ("ED9_DO_DUMP_MATINFO" in os.environ):
			import json
			with open(sys.argv[1] + ".matinfo.json", "wb") as f:
				jsondata = json.dumps(matinfo_all, indent=4).encode("utf-8")
				f.write(jsondata)

		# print("Material data total: ", f.tell(), len(dat))

	animeshiz = []
	def read_animation_data(dat):
		f = io.BytesIO(dat)
		num_of_elements = int.from_bytes(f.read(4), byteorder="little") # number of elements
		for i in range(num_of_elements):
			animation_name = read_pascal_string(f)
			animation_bone = read_pascal_string(f)
			type_int = int.from_bytes(f.read(4), byteorder="little")
			f.read(4)
			f.read(4)
			num_of_keyframes = int.from_bytes(f.read(4), byteorder="little")
			timestamps_cur = array.array('f')
			keyframes_cur = array.array('f')
			if type_int == 9: # translation
				# 36 elements per entry
				for j in range(num_of_keyframes):
					timestamp = struct.unpack('f', f.read(4))[0]
					pos_x, pos_y, pos_z = struct.unpack('fff', f.read(12))
					timestamps_cur.append(timestamp)
					keyframes_cur.extend([pos_x, pos_y, pos_z])
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
			elif type_int == 10: # rotation
				# 40 elements per entry
				for j in range(num_of_keyframes):
					timestamp = struct.unpack('f', f.read(4))[0]
					rot_x, rot_y, rot_z, rot_w = struct.unpack('ffff', f.read(16))
					timestamps_cur.append(timestamp)
					keyframes_cur.extend([rot_x, rot_y, rot_z, rot_w])
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
			elif type_int == 11: # scale
				# 36 elements per entry
				for j in range(num_of_keyframes):
					timestamp = struct.unpack('f', f.read(4))[0]
					scl_x, scl_y, scl_z = struct.unpack('fff', f.read(12))
					timestamps_cur.append(timestamp)
					keyframes_cur.extend([scl_x, scl_y, scl_z])
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
					f.read(4) # unk
			elif type_int == 12: # shader varying
				# 28 elements per entry
				for j in range(num_of_keyframes):
					f.read(28)
			elif type_int == 13: # uv scrolling
				# 32 elements per entry
				for j in range(num_of_keyframes):
					f.read(32)
			else:
				raise Exception("Unknown animation type " + str(type_int))
			if len(timestamps_cur) > 0:
				dic = {}
				dic["name"] = animation_name.decode("ASCII")
				dic["animation_bone"] = animation_bone.decode("ASCII")
				dic["timestamps"] = timestamps_cur
				dic["keyframes"] = keyframes_cur
				type_list = {
					9 : "translation",
					10 : "rotation",
					11 : "scale",
				}
				dic["type"] = type_list[type_int]
				animeshiz.append(dic)


	def read_primitive_data(dat):
		f = io.BytesIO(dat)
		num_of_elements = int.from_bytes(f.read(4), byteorder="little") # number of elements
		for i in range(num_of_elements):
			type_int = int.from_bytes(f.read(4), byteorder="little")
			size_int = int.from_bytes(f.read(4), byteorder="little")
			stride_int = int.from_bytes(f.read(4), byteorder="little")
			mesh = int.from_bytes(f.read(4), byteorder="little")
			submesh = int.from_bytes(f.read(4), byteorder="little")
			dic = {}
			dic["type_int"] = type_int
			dic["size_int"] = size_int
			dic["stride_int"] = stride_int
			dic["mesh"] = mesh
			dic["submesh"] = submesh
			primitive_shiz.append(dic)
		for i in range(num_of_elements):
			x = primitive_shiz[i]
			x["data_bytes"] = f.read(x["size_int"])

	def read_mdl_core(infn):
		with open(infn, "rb") as f:
			mdl_first_4_bytes = f.read(4)
			if mdl_first_4_bytes == b"MDL ":
				ver_ident = f.read(1) # version identify
				mdl_version.append(1 if ver_ident == b"\x01" else 2)
				f.read(1) # unk
				f.read(1) # unk
				f.read(1) # unk
				f.read(4) # unk
				chunks = []
				# chunk id
				# 0: material
				# 1: mesh
				# 2: hierarchy
				# 3: animation?
				# 0xFFFFFFFF: end
				while True:
					chunk_id_bytes = f.read(4)
					if len(chunk_id_bytes) != 4:
						raise Exception("Reached premature end of file")
					dic = {}
					chunk_id = int.from_bytes(chunk_id_bytes, byteorder="little") # chunk id (1)
					if chunk_id == 0xFFFFFFFF:
						break
					dic["chunk_id"] = chunk_id
					chunk_length = int.from_bytes(f.read(4), byteorder="little") # length of chunk data (179683)
					dic["chunk_length"] = chunk_length
					chunk_pos = f.tell()
					dic["chunk_pos"] = chunk_pos
					f.seek(chunk_length, io.SEEK_CUR)
					chunks.append(dic)
				chunk_func_dispatch = {
					0 : read_material_data,
					1 : read_mesh_data,
					2 : read_hierarchy_data,
					3 : read_animation_data,
					4 : read_primitive_data,
				}
				for chunk in chunks:
					chunk_id = chunk["chunk_id"]
					chunk_length = chunk["chunk_length"]
					chunk_pos = chunk["chunk_pos"]
					if chunk_id != 4:
						continue
					f.seek(chunk_pos)
					chunk_func_dispatch[chunk_id](f.read(chunk_length))
				for chunk in chunks:
					chunk_id = chunk["chunk_id"]
					chunk_length = chunk["chunk_length"]
					chunk_pos = chunk["chunk_pos"]
					if chunk_id != 2:
						continue
					f.seek(chunk_pos)
					chunk_func_dispatch[chunk_id](f.read(chunk_length))
				for chunk in chunks:
					chunk_id = chunk["chunk_id"]
					chunk_length = chunk["chunk_length"]
					chunk_pos = chunk["chunk_pos"]
					if chunk_id == 2 or chunk_id == 4:
						continue
					f.seek(chunk_pos)
					chunk_func_dispatch[chunk_id](f.read(chunk_length))
			else:
				
				if mdl_first_4_bytes in [b"C9BA", b"D9BA", b"F9BA"]:
					print("Model files are encrypted. Please use `kuroDecryption.py` first or use `parseKuroModel.py` instead")
				else:
					print("Not a .mdl file")

	def process_nodes():
		for node in nodes:
			node_matrix = [0.0] * 16
			compose_matrix_44(node_matrix, node["translation"], node["rotation"], node["scale"])
			node["matrix"] = node_matrix
			del node["translation"]
			del node["rotation"]
			del node["scale"]

	def process_skins():
		node_name_to_id = {}
		for i in range(len(nodes)):
			node_name_to_id[nodes[i]["name"]] = i
		mesh_id_to_node_id = {}
		for i in range(len(nodes)):
			if "mesh" in nodes[i]:
				mesh_id_to_node_id[nodes[i]["mesh"]] = i
		node_name_to_node_parent_name = {}
		for i in range(len(nodes)):
			node = nodes[i]
			if "children" in node:
				for child in node["children"]:
					node_name_to_node_parent_name[nodes[child]["name"]] = node["name"]
		node_name_to_node_id = {}
		for i in range(len(nodes)):
			node = nodes[i]
			node_name_to_node_id[node["name"]] = i
		joint_name_to_mat = {}
		if len(skins_unprocessed) > 0:
			for node in nodes:
				node_name = node["name"]
				matrix = array.array("f", node["matrix"])
				joint_name_to_mat[node_name] = matrix

		for skin_unprocessed in skins_unprocessed:
			skin = {}
			mutated_matrix_arr = []
			for name in skin_unprocessed["names"]:
				if name not in joint_name_to_mat:
					mutated_matrix_arr.append(bytes(array.array("f", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])))
					continue
				cur_matrix = joint_name_to_mat[name]
				cur_node_id = node_name_to_node_parent_name[name]
				while True:
					cur_node_matrix = joint_name_to_mat[cur_node_id]
					cur_matrix = multiply_array_as_4x4_matrix(cur_node_matrix, cur_matrix)
					if not cur_node_id in node_name_to_node_parent_name:
						break
					cur_node_id = node_name_to_node_parent_name[cur_node_id]
				cur_matrix = invert_matrix_44(cur_matrix)
				if cur_matrix == None:
					mutated_matrix_arr.append(bytes(array.array("f", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])))
					continue
				mutated_matrix_arr.append(bytes(cur_matrix))
			ibm_data = b"".join(mutated_matrix_arr)
			skin["inverseBindMatrices"] = append_vertex_data(ibm_data, data_count=len(skin_unprocessed["names"]), component_type=5126, value_type="MAT4")
			joints = []
			for name in skin_unprocessed["names"]:
				# TODO: Why are some names missing from the hierarchy?
				if name in node_name_to_id:
					joints.append(node_name_to_id[name])
				else:
					joints.append(0)
			skin["joints"] = joints
			mesh_id = skin_unprocessed["mesh_id"]
			if mesh_id in mesh_id_to_node_id:
				nodes[mesh_id_to_node_id[mesh_id]]["skin"] = len(skins)

			skins.append(skin)

	def process_animations():
		node_name_to_id = {}
		for i in range(len(nodes)):
			node_name_to_id[nodes[i]["name"]] = i
		if len(animeshiz) == 0:
			return
		for x in animeshiz:
			bone_target_name = x["animation_bone"]
			if bone_target_name in node_name_to_id:
				node_id = node_name_to_id[bone_target_name]
				x["node"] = node_id
				# node_obj = nodes[node_id]
				# if "matrix" in node_obj:
				# 	del node_obj["matrix"]

		min_timestamp = None
		# max_timestamp = None
		for x in animeshiz:
			for xx in x["timestamps"]:
				if min_timestamp == None:
					min_timestamp = xx
				if min_timestamp > xx:
					min_timestamp = xx
				# if max_timestamp == None:
				# 	max_timestamp = xx
				# if max_timestamp < xx:
				# 	max_timestamp = xx
		for x in animeshiz:
			ts = x["timestamps"]
			for i in range(len(ts)):
				ts[i] -= min_timestamp
		animation = {}
		# animation["name"] = x["name"]

		samplers = []
		animation["samplers"] = samplers

		channels = []
		animation["channels"] = channels

		for x in animeshiz:

			if "node" not in x:
				continue

			sampler = {}
			sampler["input"] = append_vertex_data(bytes(x["timestamps"]), data_count=len(x["timestamps"]), component_type=5126, value_type="SCALAR")
			sampler["output"] = append_vertex_data(bytes(x["keyframes"]), data_count=len(x["timestamps"]), component_type=5126, value_type="VEC" + str(len(x["keyframes"]) // len(x["timestamps"])))

			channel = {}
			target = {}
			target["node"] = x["node"]
			target["path"] = x["type"]
			channel["target"] = target
			channel["sampler"] = len(samplers)
			samplers.append(sampler)
			channels.append(channel)

		animations.append(animation)

		# if len(meshes) == 0:
		# 	skin = {}
		# 	joints = [x["node"] for x in animeshiz if "node" in x]
		# 	if len(joints) > 0:
		# 		skin["joints"] = joints
		# 	skins.append(skin)

	read_mdl_core(infn)
	process_nodes()
	process_skins()
	process_animations()

	if len(nodes) > 0 and len(meshes) > 0:
		import json
		import base64
		embedded_giant_buffer_joined = b"".join(embedded_giant_buffer)
		buffer0["byteLength"] = len(embedded_giant_buffer_joined)
		if False:
			with open("out.glb", "wb") as f:
				jsondata = json.dumps(gltf_data).encode("utf-8")
				jsondata += b"\x20" * (4 - (len(jsondata) % 4)) # padding
				f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(jsondata) + 8 + len(embedded_giant_buffer_joined)))
				f.write(struct.pack("<II", len(jsondata), 0x4E4F534A))
				f.write(jsondata)
				f.write(struct.pack("<II", len(embedded_giant_buffer_joined), 0x004E4942))
				f.write(embedded_giant_buffer_joined)
		else:
			buffer0["uri"] = (b"data:application/octet-stream;base64," + base64.b64encode(embedded_giant_buffer_joined)).decode("ASCII")
			with open(infn[:-4] + ".gltf", "wb") as f:
				jsondata = json.dumps(gltf_data, indent=4).encode("utf-8")
				f.write(jsondata)
	
		if len(all_images) > 0:
			all_images = list(all_images)
			with open(infn[:-4] + "_images.txt", "w") as f:
				f.write(json.dumps(all_images))

if __name__ == "__main__":
	read_mdl_to_gltf(sys.argv[1])
