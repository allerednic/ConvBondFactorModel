from pathlib import Path

_proj_path = Path(__file__).absolute().parent.parent
_data_path = str(_proj_path.parent.joinpath('Data'))
_test_path = str(_proj_path.joinpath('tests'))
