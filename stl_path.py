import sys, os

cur_dir = os.path.dirname(__file__)

trex_path = os.path.abspath('/opt/trex/v2.88/automation/trex_control_plane/interactive')
sys.path.insert(0, os.path.abspath(trex_path))

STL_PROFILES_PATH = os.path.join('/opt/trex/v2.88/stl')
EXT_LIBS_PATH = os.path.abspath('/opt/trex/v2.88/external_libs')
assert os.path.isdir(STL_PROFILES_PATH), 'Could not determine STL profiles path'
assert os.path.isdir(EXT_LIBS_PATH), 'Could not determine external_libs path'


