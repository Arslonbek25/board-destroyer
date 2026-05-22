import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clock import Clock


def make_config(
    min_time=0.1,
    max_time=10.0,
    skill_level=3,
    time_advantage=0,
    k=0.3,
    randomness_factor=0.0,
    phase_factors=None,
):
    tc = SimpleNamespace(
        min_time=min_time, max_time=max_time, skill_level=skill_level, depth=None
    )
    cfg = SimpleNamespace(
        time_control=tc,
        time_advantage=time_advantage,
        k=k,
        randomness_factor=randomness_factor,
        phase_factors=phase_factors
        or {"opening": 1.0, "middlegame": 1.0, "endgame": 1.0, "late_endgame": 1.0},
    )
    return cfg


def test_phase_boundaries():
    c = Clock(make_config())
    assert c.get_phase(32) == "opening"
    assert c.get_phase(28) == "opening"
    assert c.get_phase(27) == "middlegame"
    assert c.get_phase(16) == "middlegame"
    assert c.get_phase(15) == "endgame"
    assert c.get_phase(6) == "endgame"
    assert c.get_phase(5) == "late_endgame"
    assert c.get_phase(2) == "late_endgame"


def test_move_time_capped_by_max():
    c = Clock(make_config(min_time=0.1, max_time=5.0))
    for opp in [0.5, 1.0, 5.0, 20.0]:
        t = c.calculate_move_time(opp, num_pieces=20)
        assert t <= 5.0 + 1e-9


def test_min_time_floor_overrides_opp_clamp_when_opp_is_faster():
    # Documents the clamp order in calculate_move_time: after the opp-time
    # bound, min_time is reapplied — so when opp moves faster than min_time,
    # the bot still spends at least min_time (engine-quality floor).
    c = Clock(make_config(min_time=0.5, max_time=5.0))
    t = c.calculate_move_time(opponents_move_time=0.01, num_pieces=20)
    assert t >= 0.5 - 1e-9


def test_min_time_floor_when_opponent_above_min():
    c = Clock(make_config(min_time=0.2, max_time=5.0))
    t = c.calculate_move_time(opponents_move_time=0.25, num_pieces=20)
    assert t >= 0.2 - 1e-9


def test_phase_factor_reduces_effective_max():
    # opening factor 0.1 → effective max becomes max_time * 0.1
    pf = {"opening": 0.1, "middlegame": 1.0, "endgame": 1.0, "late_endgame": 1.0}
    c = Clock(make_config(min_time=0.1, max_time=10.0, phase_factors=pf))
    # opp_move long enough that without the factor we'd ride near max_time
    t = c.calculate_move_time(opponents_move_time=8.0, num_pieces=32)
    assert t <= 1.0 + 1e-9  # capped by 10 * 0.1


def test_bot_does_not_exceed_opp_time_when_min_time_allows():
    # When min_time is below the opp time, the opp-time clamp wins.
    c = Clock(make_config(min_time=0.01, max_time=10.0))
    t = c.calculate_move_time(opponents_move_time=0.05, num_pieces=20)
    assert t <= 0.05 + 1e-9


def test_time_advantage_drives_bot_below_opponent_total():
    # 90% time advantage: bot should end up using far less than opponent over time
    c = Clock(make_config(time_advantage=90, min_time=0.01, max_time=10.0))
    for _ in range(20):
        c.calculate_move_time(opponents_move_time=2.0, num_pieces=20)
    # desired = 0.1 * opponent_total; with adjustment, bot_total should be well below opp_total
    assert c.bot_total_time < c.opponent_total_time


def test_zero_time_advantage_does_not_aggressively_clamp_down():
    # With 0% time advantage, the adjustment branch should rarely engage
    c = Clock(make_config(time_advantage=0, min_time=0.01, max_time=10.0))
    times = [c.calculate_move_time(opponents_move_time=1.0, num_pieces=20) for _ in range(10)]
    # all reasonably similar — no runaway downward drift
    assert max(times) - min(times) < 1.0


def test_accumulators_track_consumption():
    c = Clock(make_config())
    c.calculate_move_time(opponents_move_time=1.5, num_pieces=20)
    assert c.opponent_total_time == 1.5
    c.calculate_move_time(opponents_move_time=2.0, num_pieces=20)
    assert c.opponent_total_time == 3.5
    assert c.bot_total_time > 0
