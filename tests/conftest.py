def pytest_addoption(parser):
    parser.addoption(
        "--target-class", action="store", default=None,
        help="Restricts test_leveling_playthrough_single.py to this class "
             "(e.g. --target-class=Warrior) instead of editing DEFAULT_TARGET_CLASS in that file.",
    )
