import io
from qsv import main
from qsv.controllers.DataFrameController import DataFrameController
import polars

scriptpath = '__init__.py'
logpath = 'Security.csv'

def test_load_unit():
    d = DataFrameController()
    d.load(logpath)
    assert type(d.df) == polars.lazyframe.frame.LazyFrame

def test_load_cli(monkeypatch):
    argv = [scriptpath, "load", logpath]
    stdin = io.StringIO()
    stdout = io.StringIO()

    with monkeypatch.context() as m:
        m.setattr("sys.argv", argv)
        m.setattr("sys.stdin", stdin)
        m.setattr("sys.stdout", stdout)
        main()
        assert stdout.getvalue().startswith('shape: ')

def test_load_quilt(tmpdir, monkeypatch):
    config = """title: test
rules:
    load:
"""
    temp_file = tmpdir.join('tmprule.yaml')
    temp_file.write(config)

    argv = [scriptpath, "quilt", str(temp_file), logpath]
    stdin = io.StringIO()
    stdout = io.StringIO()

    with monkeypatch.context() as m:
        m.setattr("sys.argv", argv)
        m.setattr("sys.stdin", stdin)
        m.setattr("sys.stdout", stdout)
        main()
        assert stdout.getvalue().startswith('Loaded Rules')