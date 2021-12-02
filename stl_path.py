import sys, os
from dotenv import load_dotenv

load_dotenv()

cur_dir = os.path.dirname(__file__)

trex_path = f"{os.getenv('TREX_LOCATION')}/{os.getenv('TREX_VERSION')}"
interactive = os.path.abspath(f"{trex_path}/automation/trex_control_plane/interactive")

sys.path.insert(0, os.path.abspath(trex_path))

STL_PROFILES_PATH = os.path.join(f"{trex_path}/stl")
EXT_LIBS_PATH = os.path.abspath(f"{trex_path}/external_libs")
assert os.path.isdir(STL_PROFILES_PATH), "Could not determine STL profiles path"
assert os.path.isdir(EXT_LIBS_PATH), "Could not determine external_libs path"
