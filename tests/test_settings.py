from polyethylene_tank.settings import Tiempos, cargar, guardar


def test_missing_file_gives_defaults(tmp_path):
    assert cargar(tmp_path / "no-existe.json") == Tiempos()


def test_round_trip(tmp_path):
    path = tmp_path / "sub" / "tiempos.json"
    guardar(path, Tiempos(llenado=20, limpieza=30, desfogue=5))
    assert cargar(path) == Tiempos(llenado=20, limpieza=30, desfogue=5)


def test_corrupt_or_invalid_file_gives_defaults(tmp_path):
    path = tmp_path / "tiempos.json"
    path.write_text("{no es json", encoding="utf-8")
    assert cargar(path) == Tiempos()
    path.write_text('{"llenado": 9999}', encoding="utf-8")
    assert cargar(path) == Tiempos()
