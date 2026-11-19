
# test_bug3_logic.py
# 실행: pytest -v test_bug3_logic.py

import pytest

from bug3_logic import find_max, count_pass


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ([70, 85, 60, 95], 95),  # 마지막 원소가 최댓값
        ([95, 70, 85, 60], 95),  # 첫 번째 원소가 최댓값
        ([70, 95, 85, 60], 95),  # 중간 원소가 최댓값
        ([10, 20], 20),         # 원소가 두 개이고 마지막이 최댓값
        ([20, 10], 20),
        ([42], 42),             # 원소가 하나인 리스트
        ([-10, -3, -20, -1], -1),  # 음수만 있는 리스트
        ([-5, 0, -2], 0),       # 0이 최댓값
        ([80, 80, 80], 80),     # 모든 원소가 같음
        ([95, 60, 95], 95),     # 최댓값이 중복됨
    ],
)
def test_find_max(scores, expected):
    assert find_max(scores) == expected


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ([70, 85, 60, 95], 4),  # 기본 기준값 60도 합격에 포함
        ([59, 60, 61], 2),      # 기준값 직전, 동일, 직후
        ([60], 1),
        ([59], 0),
        ([61], 1),
        ([60, 60, 60], 3),      # 기준값과 같은 점수가 여러 개
        ([0, 30, 59], 0),       # 전원 기준 미달
        ([61, 80, 100], 3),     # 전원 기준 초과
        ([], 0),               # 빈 리스트에는 합격자가 없음
    ],
)
def test_count_pass_default_cutoff(scores, expected):
    assert count_pass(scores) == expected


@pytest.mark.parametrize(
    ("scores", "cutoff", "expected"),
    [
        ([70, 85, 60, 95], 85, 2),
        ([79, 80, 81], 80, 2),  # 사용자 지정 기준값도 포함
        ([0, 1, -1], 0, 2),     # 기준값이 0
        ([-3, -2, -1], -2, 2),  # 음수 기준값
        ([0, 99, 100], 100, 1),
        ([70, 85, 95], 100, 0),
        ([70, 85, 95], 50, 3),
        ([], 80, 0),
    ],
)
def test_count_pass_custom_cutoff(scores, cutoff, expected):
    assert count_pass(scores, cutoff=cutoff) == expected


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
