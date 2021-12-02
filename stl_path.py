import sys, os
from dotenv import dotenv_values

config = dotenv_values(".env")

cur_dir = os.path.dirname(__file__)

trex_path = f"{config['TREX_LOCATION']}/{config['TREX_VERSION']}"
interactive = os.path.abspath(f"{trex_path}/automation/trex_control_plane/interactive")

sys.path.insert(0, os.path.abspath(interactive))

STL_PROFILES_PATH = os.path.join(f"{trex_path}/stl")
EXT_LIBS_PATH = os.path.abspath(f"{trex_path}/external_libs")
assert os.path.isdir(STL_PROFILES_PATH), "Could not determine STL profiles path"
assert os.path.isdir(EXT_LIBS_PATH), "Could not determine external_libs path"
