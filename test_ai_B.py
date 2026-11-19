# test_load_scores.py
# 실행: pytest -v test_load_scores.py
# load_scores.py와 같은 디렉터리에 저장하세요.

import pytest

from load_scores import load_scores


def _write_csv(tmp_path, content):
    path = tmp_path / "scores.csv"
    path.write_text(content, encoding="utf-8")
    return path


def _assert_result(actual, expected_kept, expected_skipped):
    """반환 구조, 데이터 순서, 제외 기록을 검사한다."""
    assert isinstance(actual, tuple)
    assert len(actual) == 2

    kept, skipped = actual
    assert isinstance(kept, list)
    assert isinstance(skipped, list)
    assert kept == expected_kept

    for student in kept:
        assert isinstance(student, tuple)
        assert len(student) == 2
        assert isinstance(student[0], str)
        assert type(student[1]) is int

    assert len(skipped) == len(expected_skipped)

    for record, expected in zip(skipped, expected_skipped):
        assert isinstance(record, tuple)
        assert len(record) == 3

        line_number, original_line, reason = record
        expected_number, expected_line, expected_reason = expected

        assert type(line_number) is int
        assert line_number == expected_number
        assert isinstance(original_line, str)

        # 명세에는 원본줄의 줄바꿈 포함 여부가 정해져 있지 않으므로
        # 줄바꿈 유무는 허용하되, 그 외 공백과 원문은 그대로 검사한다.
        assert original_line in (
            expected_line,
            expected_line + "\n",
            expected_line + "\r\n",
        )
        assert reason == expected_reason


def test_normal_students(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"
        "김정민,85\n"
        "이수진,92\n"
        "박민수,73\n",
    )

    _assert_result(
        load_scores(path),
        [("김정민", 85), ("이수진", 92), ("박민수", 73)],
        [],
    )


def test_missing_file_raises_file_not_found_error(tmp_path):
    path = tmp_path / "missing.csv"
    assert not path.exists()

    with pytest.raises(FileNotFoundError):
        load_scores(path)


@pytest.mark.parametrize("content", ["name,score\n", "name,score"])
def test_header_only_returns_empty_lists(tmp_path, content):
    path = _write_csv(tmp_path, content)

    _assert_result(load_scores(path), [], [])


def test_strips_surrounding_spaces_from_name_and_score(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"
        "  김정민  ,  85  \n"
        '"  이수진  ","  92  "\n',
    )

    _assert_result(
        load_scores(path),
        [("김정민", 85), ("이수진", 92)],
        [],
    )


def test_quoted_name_containing_comma(tmp_path):
    path = _write_csv(
        tmp_path,
        'name,score\n'
        '"Kim, Jungmin",90\n'
        '"홍, 길동",80\n',
    )

    _assert_result(
        load_scores(path),
        [("Kim, Jungmin", 90), ("홍, 길동", 80)],
        [],
    )


def test_duplicate_names_are_all_kept(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"
        "김정민,80\n"
        "이수진,90\n"
        "김정민,95\n"
        "김정민,80\n",
    )

    _assert_result(
        load_scores(path),
        [("김정민", 80), ("이수진", 90), ("김정민", 95), ("김정민", 80)],
        [],
    )


@pytest.mark.parametrize(
    ("score", "valid"),
    [("0", True), ("100", True), ("101", False), ("-1", False)],
    ids=["minimum-0", "maximum-100", "above-maximum-101", "below-minimum-minus1"],
)
def test_score_boundaries(tmp_path, score, valid):
    row = f"김정민,{score}"
    path = _write_csv(tmp_path, f"name,score\n{row}\n")

    if valid:
        _assert_result(load_scores(path), [("김정민", int(score))], [])
    else:
        _assert_result(
            load_scores(path),
            [],
            [(2, row, "점수가 0~100 밖")],
        )


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ("김정민", "열 개수가 2가 아님"),
        ("김정민,90,추가", "열 개수가 2가 아님"),
        ("김정민,90,", "열 개수가 2가 아님"),
        (",90", "이름이 비어 있음"),
        ("   ,90", "이름이 비어 있음"),
        ("김정민,", "점수가 비어 있음"),
        ("김정민,   ", "점수가 비어 있음"),
        ("김정민,abc", "점수가 정수가 아님"),
        ("김정민,90.5", "점수가 정수가 아님"),
        ("김정민,90.0", "점수가 정수가 아님"),
    ],
)
def test_invalid_rows_are_recorded(tmp_path, row, reason):
    path = _write_csv(tmp_path, f"name,score\n{row}\n")

    _assert_result(load_scores(path), [], [(2, row, reason)])


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        (",,추가", "열 개수가 2가 아님"),
        (",", "이름이 비어 있음"),
        (",abc", "이름이 비어 있음"),
        (",101", "이름이 비어 있음"),
        ("   ,   ", "이름이 비어 있음"),
    ],
)
def test_validation_order(tmp_path, row, reason):
    """여러 오류가 있어도 명세의 검증 순서에 따른 첫 사유를 기록한다."""
    path = _write_csv(tmp_path, f"name,score\n{row}\n")

    _assert_result(load_scores(path), [], [(2, row, reason)])


def test_blank_lines_are_ignored_and_physical_line_numbers_are_preserved(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"       # 1
        "\n"                 # 2
        "김정민,80\n"        # 3
        "\n"                 # 4
        "이수진,abc\n"       # 5
        "\n"                 # 6
        "박민수,100\n"       # 7
        "\n",                # 8
    )

    _assert_result(
        load_scores(path),
        [("김정민", 80), ("박민수", 100)],
        [(5, "이수진,abc", "점수가 정수가 아님")],
    )


def test_mixed_rows_preserve_order_and_original_text(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"                  # 1
        "김정민,0\n"                    # 2
        "  제외학생  , 101  \n"          # 3
        '"Kim, Jungmin",100\n'           # 4
        "이수진,90,추가\n"               # 5
        "\n"                            # 6
        "김정민,85\n"                   # 7
        '"잘못된, 이름",abc\n'          # 8
        "박민수,70\n"                   # 9
        ",80\n"                         # 10
        "최유진,\n",                    # 11
    )

    _assert_result(
        load_scores(path),
        [
            ("김정민", 0),
            ("Kim, Jungmin", 100),
            ("김정민", 85),
            ("박민수", 70),
        ],
        [
            (3, "  제외학생  , 101  ", "점수가 0~100 밖"),
            (5, "이수진,90,추가", "열 개수가 2가 아님"),
            (8, '"잘못된, 이름",abc', "점수가 정수가 아님"),
            (10, ",80", "이름이 비어 있음"),
            (11, "최유진,", "점수가 비어 있음"),
        ],
    )


def test_last_data_row_without_trailing_newline(tmp_path):
    path = _write_csv(tmp_path, "name,score\n김정민,100\n이수진,101")

    _assert_result(
        load_scores(path),
        [("김정민", 100)],
        [(3, "이수진,101", "점수가 0~100 밖")],
    )


def test_input_file_is_not_modified(tmp_path):
    path = _write_csv(
        tmp_path,
        "name,score\n"
        "  김정민  , 85 \n"
        "\n"
        '"Kim, Jungmin",100\n'
        "이수진,101\n"
        "박민수,abc\n",
    )
    original_bytes = path.read_bytes()

    load_scores(path)

    assert path.read_bytes() == original_bytes


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))