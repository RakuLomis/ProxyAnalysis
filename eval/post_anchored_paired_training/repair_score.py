"""Run the unchanged preregistered scorer on the explicitly repaired view."""
import common
import score


def main():
    path = common.OUT/'repair-v1'
    common.OUT = path; score.OUT = path
    score.main()


if __name__ == '__main__': main()
