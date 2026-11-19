# test_load_scores.py
# 실행: pytest -v test_load_scores.py
# load_scores.py와 같은 폴더에 저장하세요.

import pytest

from load_scores import load_scores


@pytest.fixture
def make_csv(tmp_path):
    """임시 폴더에 테스트용 CSV 파일을 만든다."""
    def _make_csv(content, encoding="utf-8"):
        path = tmp_path / "scores.csv"
        path.write_text(content, encoding=encoding)
        return path

    return _make_csv


def test_normal_input(make_csv):
    """정상 데이터는 입력 순서대로 저장하고 점수를 정수로 반환한다."""
    path = make_csv(
        "이름,점수\n"
        "김정민,95\n"
        "이민수,80\n"
    )

    kept, skipped = load_scores(path)

    assert kept == [("김정민", 95), ("이민수", 80)]
    assert skipped == []
    assert all(type(score) is int for _, score in kept)


def test_file_not_found(tmp_path):
    """없는 파일의 FileNotFoundError를 숨기지 않는다."""
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(path)


def test_header_only(make_csv):
    """헤더만 있으면 두 개의 빈 리스트를 반환한다."""
    path = make_csv("이름,점수\n")

    assert load_scores(path) == ([], [])


@pytest.mark.parametrize(
    "score, expected_kept, expected_skipped",
    [
        (0, [("김정민", 0)], []),
        (100, [("김정민", 100)], []),
        (101, [], [(2, "김정민,101", "점수가 0~100 밖")]),
        (-1, [], [(2, "김정민,-1", "점수가 0~100 밖")]),
    ],
)
def test_score_boundaries(
    make_csv, score, expected_kept, expected_skipped
):
    """0과 100은 허용하고, 101과 -1은 건너뛴다."""
    path = make_csv(f"이름,점수\n김정민,{score}\n")

    assert load_scores(path) == (expected_kept, expected_skipped)


@pytest.mark.parametrize(
    "original, reason",
    [
        ("김정민", "열 개수가 2가 아님"),
        ("김정민,90,추가", "열 개수가 2가 아님"),
        ("김정민,", "점수가 비어 있음"),
        ("김정민,   ", "점수가 비어 있음"),
        ("김정민,abc", "점수가 정수가 아님"),
        ("김정민,90.5", "점수가 정수가 아님"),
        (",90", "이름이 비어 있음"),
        ("   ,90", "이름이 비어 있음"),
    ],
)
def test_invalid_rows(make_csv, original, reason):
    """잘못된 줄을 기록한 뒤에도 다음 정상 줄을 계속 읽는다."""
    path = make_csv(
        "이름,점수\n"
        f"{original}\n"
        "정상학생,75\n"
    )

    kept, skipped = load_scores(path)

    assert kept == [("정상학생", 75)]
    assert skipped == [(2, original, reason)]


def test_duplicate_names_are_preserved(make_csv):
    """이름과 점수가 같더라도 중복 데이터를 제거하지 않는다."""
    path = make_csv(
        "이름,점수\n"
        "김정민,90\n"
        "김정민,80\n"
        "김정민,90\n"
    )

    kept, skipped = load_scores(path)

    assert kept == [
        ("김정민", 90),
        ("김정민", 80),
        ("김정민", 90),
    ]
    assert skipped == []


def test_blank_lines_are_ignored(make_csv):
    """빈 줄은 기록하지 않으며 이후 오류의 줄번호는 유지한다."""
    path = make_csv(
        "이름,점수\n"   # 1행
        "\n"            # 2행
        "김정민,95\n"   # 3행
        "\n"            # 4행
        "이민수,abc\n"  # 5행
        "\n"            # 6행
    )

    kept, skipped = load_scores(path)

    assert kept == [("김정민", 95)]
    assert skipped == [(5, "이민수,abc", "점수가 정수가 아님")]


def test_surrounding_whitespace_is_removed(make_csv):
    """이름과 점수 양끝의 공백을 제거한다."""
    path = make_csv(
        "이름,점수\n"
        "  김정민  ,  95  \n"
    )

    assert load_scores(path) == ([("김정민", 95)], [])


def test_utf8_bom_file(make_csv):
    """UTF-8 BOM이 있는 CSV도 정상적으로 읽는다."""
    path = make_csv(
        "이름,점수\n김정민,95\n",
        encoding="utf-8-sig",
    )

    assert load_scores(path) == ([("김정민", 95)], [])


def test_mixed_valid_and_invalid_rows(make_csv):
    """정상·오류 데이터가 섞여도 목록과 오류 기록의 순서를 유지한다."""
    path = make_csv(
        "이름,점수\n"    # 1행
        "김정민,0\n"     # 2행
        "이민수,101\n"   # 3행
        ",80\n"          # 4행
        "박지수,100\n"   # 5행
        "최유진,abc\n"   # 6행
        "김정민,90\n"    # 7행
    )

    kept, skipped = load_scores(path)

    assert kept == [
        ("김정민", 0),
        ("박지수", 100),
        ("김정민", 90),
    ]
    assert skipped == [
        (3, "이민수,101", "점수가 0~100 밖"),
        (4, ",80", "이름이 비어 있음"),
        (6, "최유진,abc", "점수가 정수가 아님"),
    ]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))