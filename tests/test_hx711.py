import pytest

from polyethylene_tank import hx711 as hx711_module
from polyethylene_tank.hx711 import HX711


class FakeChip:
    """Simula un HX711: entrega `value` (24 bits) un bit por pulso de SCK."""

    def __init__(self, value, ready=True, frame=25):
        self.bits = format(value & 0xFFFFFF, "024b")
        self.frame = frame  # pulsos por lectura: 24 + los de ganancia
        self.ready = ready
        self.pulses = 0
        self.total_pulses = 0
        self.dout_state = 0 if ready else 1
        self.dout = FakeDout(self)
        self.sck = FakeSck(self)

    def clock(self, state):
        if not state:
            return
        self.dout_state = int(self.bits[self.pulses]) if self.pulses < 24 else 1
        self.pulses += 1
        self.total_pulses += 1
        if self.pulses == self.frame:  # fin de la lectura: nueva conversión lista
            self.pulses = 0
            self.dout_state = 0 if self.ready else 1


class FakeDout:
    function = None

    def __init__(self, chip):
        self.chip = chip

    @property
    def state(self):
        return self.chip.dout_state

    def close(self):
        pass


class FakeSck:
    function = None

    def __init__(self, chip):
        self.chip = chip

    @property
    def state(self):
        return 0

    @state.setter
    def state(self, value):
        self.chip.clock(value)

    def close(self):
        pass


def make(value, gain=128, ready=True):
    chip = FakeChip(value, ready, frame=24 + {128: 1, 32: 2, 64: 3}.get(gain, 1))
    return chip, HX711(chip.dout, chip.sck, gain)


@pytest.mark.parametrize("value", [0, 1000, 0x7FFFFE, -1000, -0x7FFFFF])
def test_read_raw_decodes_signed_24_bits(value):
    _, hx = make(value)
    assert hx.read_raw() == value


@pytest.mark.parametrize(("gain", "pulses"), [(128, 25), (32, 26), (64, 27)])
def test_gain_selects_extra_pulses(gain, pulses):
    chip, hx = make(1234, gain)
    assert hx.read_raw() == 1234
    assert chip.total_pulses == pulses


def test_invalid_gain():
    with pytest.raises(ValueError, match="ganancia"):
        make(0, gain=100)


def test_timeout_when_chip_never_ready():
    _, hx = make(0, ready=False)
    with pytest.raises(TimeoutError):
        hx.read_raw(timeout=0.01)


def test_stuck_high_line_is_invalid():
    _, hx = make(0xFFFFFF)  # cable suelto: DOUT siempre en alto
    assert hx.read_raw() is None


def test_long_clock_pulse_discards_sample(monkeypatch):
    ticks = iter(range(0, 10**9, 100_000))  # cada llamada avanza 100 µs
    monkeypatch.setattr(hx711_module, "perf_counter_ns", lambda: next(ticks))
    _, hx = make(1000)
    assert hx.read_raw() is None


def test_tare_and_weight():
    chip, hx = make(1000)
    hx.tare(seconds=0)
    assert hx.offset == 1000

    chip.bits = format(3000, "024b")
    hx.reference_unit = 2
    assert hx.weight(seconds=0) == 1000
