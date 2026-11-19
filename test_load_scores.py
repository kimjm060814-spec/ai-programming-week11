import pytest

from helpers import 쓰기
from load_scores import load_scores


# 정상 ①: 정상 학생 5명이 있는 CSV
def test_정상_학생_5명을_읽는다(tmp_path):
    path = tmp_path / "normal.csv"
    path.write_text(
        "name,score\n"
        "김하나,88\n"
        "이두리,75\n"
        "박세찬,60\n"
        "윤보람,64\n"
        "서한별,95\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    print("정상 파일 결과:", kept, skipped)

    assert kept == [
        ("김하나", 88),
        ("이두리", 75),
        ("박세찬", 60),
        ("윤보람", 64),
        ("서한별", 95),
    ]
    assert skipped == []


# 정상 ②: 빈 줄은 기록 없이 무시
def test_빈_줄을_무시한다(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text(
        "name,score\n"
        "김하나,88\n"
        "\n"
        "윤보람,64\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    print("빈 줄 포함 결과:", kept, skipped)

    assert kept == [("김하나", 88), ("윤보람", 64)]
    assert skipped == []


# 정상 ③: 따옴표로 감싼 이름 안의 쉼표 처리
def test_쉼표가_있는_이름을_읽는다(tmp_path):
    path = tmp_path / "comma.csv"
    path.write_text(
        'name,score\n"김, 하나",88\n',
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    print("쉼표 이름 결과:", kept, skipped)

    assert kept == [("김, 하나", 88)]
    assert skipped == []


# 예외 ①: 없는 파일은 FileNotFoundError
def test_없는_파일은_예외가_발생한다(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(path)


# 예외 ②: 헤더만 있으면 두 목록 모두 비어 있음
def test_헤더만_있으면_빈_목록을_반환한다(tmp_path):
    path = tmp_path / "header_only.csv"
    path.write_text("name,score\n", encoding="utf-8")

    kept, skipped = load_scores(path)

    print("헤더만 있는 결과:", kept, skipped)

    assert kept == []
    assert skipped == []


# 경계 ①~③: 0, 100은 포함하고 101은 제외
@pytest.mark.parametrize(
    "score, expected_kept, expected_skipped",
    [
        (0, [("홍길동", 0)], []),
        (100, [("홍길동", 100)], []),
        (
            101,
            [],
            [(2, "홍길동,101", "점수가 0~100 밖")],
        ),
    ],
)
def test_점수_경계값(
    tmp_path, score, expected_kept, expected_skipped
):
    path = tmp_path / "boundary.csv"
    쓰기(path, score)

    kept, skipped = load_scores(path)

    print(f"{score}점 결과:", kept, skipped)

    assert kept == expected_kept
    assert skipped == expected_skipped
# 추가 검사: 잘못된 입력을 제외하고 사유를 기록하는지 확인
@pytest.mark.parametrize(
    "data_line, expected_reason",
    [
        ("홍길동,80,추가", "열 개수가 2가 아님"),
        (",80", "이름이 비어 있음"),
        ("홍길동,", "점수가 비어 있음"),
        ("홍길동,결석", "점수가 정수가 아님"),
    ],
)
def test_잘못된_입력을_제외하고_기록한다(
    tmp_path, data_line, expected_reason
):
    path = tmp_path / "invalid.csv"
    path.write_text(
        f"name,score\n{data_line}\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    print("입력:", data_line)
    print("유효 데이터:", kept)
    print("제외 기록:", skipped)

    assert kept == []
    assert skipped == [(2, data_line, expected_reason)]
# 추가 검사: 잘못된 입력을 제외하고 사유를 기록하는지 확인
@pytest.mark.parametrize(
    "data_line, expected_reason",
    [
        ("홍길동,80,추가", "열 개수가 2가 아님"),
        (",80", "이름이 비어 있음"),
        ("홍길동,", "점수가 비어 있음"),
        ("홍길동,결석", "점수가 정수가 아님"),
    ],
)
def test_잘못된_입력을_제외하고_기록한다(
    tmp_path, data_line, expected_reason
):
    path = tmp_path / "invalid.csv"
    path.write_text(
        f"name,score\n{data_line}\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(path)

    print("입력:", data_line)
    print("유효 데이터:", kept)
    print("제외 기록:", skipped)

    assert kept == []
    assert skipped == [(2, data_line, expected_reason)]