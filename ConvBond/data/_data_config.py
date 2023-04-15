from pathlib import Path
import platform

os_info = platform.system() 

_project_path = Path(__file__).absolute().parent
_data_path = str(_project_path.parent)
