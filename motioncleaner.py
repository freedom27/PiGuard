from actions import IAction
from piguardtyping import Status


class MotionCleaner(IAction):

    def perform_action(self, status: Status):
        status["motion"] = False


def fet_motion_cleaner():
    return MotionCleaner()
