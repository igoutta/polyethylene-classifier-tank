from polyethylene_tank import weight
from polyethylene_tank.weight import leer, publicar


def test_round_trip(tmp_path):
    path = tmp_path / "peso.json"
    publicar(250.5, path)
    assert leer(path) == 250.5


def test_missing_file_is_no_data(tmp_path):
    assert leer(tmp_path / "no-existe.json") is None


def test_stale_reading_is_no_data(tmp_path, monkeypatch):
    path = tmp_path / "peso.json"
    publicar(250.5, path)
    reloj = weight.time() + 60  # un minuto después
    monkeypatch.setattr(weight, "time", lambda: reloj)
    assert leer(path, max_edad=5) is None


def test_corrupt_file_is_no_data(tmp_path):
    path = tmp_path / "peso.json"
    for contenido in ("{no es json", "[]", '{"peso": "x", "t": 0}', '{"t": 1}'):
        path.write_text(contenido, encoding="utf-8")
        assert leer(path) is None
