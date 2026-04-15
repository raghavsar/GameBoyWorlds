from gameboy_worlds.utils import log_info
from gameboy_worlds.emulation.tracker import (
    DummySubGoalMetric,
    StateTracker,
    TestTrackerMixin,
    make_subgoal_metric_class,
)
from gameboy_worlds.emulation.deja_vu.parsers import AgentState
from gameboy_worlds.emulation.deja_vu.base_metrics import (
    DejaVuTestMetric,
    CoreDejaVuMetrics,
    DejaVuOCRMetric,
)
# import metrics for the test trackers
from gameboy_worlds.emulation.deja_vu.test_metrics import (
    CheckedCoatTerminationMetric,
    CheckedGunTerminationMetric,
    ClosedPocketTerminationMetric,
    ClosedWalletTerminationMetric,
    EnterCellarTerminationMetric,
    HitBottleTerminationMetric,
    OpenDoorTerminationMetric,
    OpenPocketTerminationMetric,
    OpenSpigotTerminationMetric,
    OpenWalletTerminationMetric,
    TakeCoatTerminationMetric,
    TakeGunTerminationMetric,
    CloseDoorTerminationMetric,
)
# import subgoal classes for the subgoal metrics
from gameboy_worlds.emulation.deja_vu.test_metrics import (
    SelectedOpenActionInMenuSubGoal,
    SelectedOpenActionInNormalSubGoal,
    SelectedTakeActionInNormalSubGoal,
    SelectedCloseActionInNormalSubGoal,
    NoActionSelectedInNormalSubGoal,
    SelectedCloseActionInMenuSubGoal,
    InCoatPocketMenuSubGoal,
    InWalletMenuSubGoal,
    PointAtCoatSubGoal,
    PointAtWalletSubGoal,
    InGoodsMenuSubGoal,
    SelectedHitActionInNormalSubGoal,
    SockoOnScreenSubGoal,
    OpenedCellarDoorOnScreenSubGoal,
)


class CoreDejaVuTracker(StateTracker):
    """
    StateTracker for core Deja Vu metrics.
    """

    _REMOVE_GRID_OVERLAY = False
    """ Whether to remove the grid overlay drawn by the state parser when the agent is in FREE ROAM. This is useful for VLM based agents may need a coordinate grid overlayed onto the frame, but may cause issues for agents that do not understand that it is not a part of the game. """

    def start(self):
        super().start()
        self.metric_classes.extend([CoreDejaVuMetrics, DejaVuTestMetric])

    def step(self, *args, **kwargs):
        """
        Calls on super().step(), but then modifies the current frame to overlay the grid if the agent is in FREE ROAM.
        """
        super().step(*args, **kwargs)

        if self._REMOVE_GRID_OVERLAY:
            state = self.episode_metrics["dejavu_core"]["agent_state"]
            # if agent_state is in FREE ROAM, draw the grid, otherwise do not
            if state == AgentState.FREE_ROAM:
                screen = self.episode_metrics["core"]["current_frame"]
                screen = self.state_parser.draw_grid_overlay(current_frame=screen)
                self.episode_metrics["core"]["current_frame"] = screen
                previous_screens = self.episode_metrics["core"]["passed_frames"]
                if previous_screens is not None:
                    self.episode_metrics["core"]["passed_frames"][-1, :] = screen


class DejaVuOCRTracker(CoreDejaVuTracker):
    def start(self):
        super().start()
        self.metric_classes.extend([DejaVuOCRMetric])


class DejaVuTestTracker(TestTrackerMixin, DejaVuOCRTracker):
    """
    Inherit this class and set TERMINATION_TRUNCATION_METRIC to create a TestTracker for Deja Vu games.
    """

    TERMINATION_TRUNCATION_METRIC = TakeCoatTerminationMetric
    SUBGOAL_METRIC = DummySubGoalMetric


class DejaVuCoatTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent takes the coat.
    """

    TERMINATION_TRUNCATION_METRIC = TakeCoatTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([SelectedTakeActionInNormalSubGoal])

class DejaVuTakeGunTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent takes the gun.
    """

    TERMINATION_TRUNCATION_METRIC = TakeGunTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([SelectedTakeActionInNormalSubGoal])

class DejaVuOpenDoorTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent opens the door.
    """

    TERMINATION_TRUNCATION_METRIC = OpenDoorTerminationMetric
    SUBGOAL_METRIC = DummySubGoalMetric
    # make_subgoal_metric_class([SelectedOpenActionInNormalSubGoal, NoActionSelectedInNormalSubGoal])

class DejaVuCloseDoorTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent closes the door.
    """

    TERMINATION_TRUNCATION_METRIC = CloseDoorTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([SelectedCloseActionInNormalSubGoal])

class DejaVuOpenPocketTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent opens the pocket.
    """

    TERMINATION_TRUNCATION_METRIC = OpenPocketTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([SelectedOpenActionInMenuSubGoal])

class DejaVuOpenWalletTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent opens the wallet.
    """

    TERMINATION_TRUNCATION_METRIC = OpenWalletTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([SelectedOpenActionInMenuSubGoal])

class DejaVuClosePocketTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent closes the pocket.
    """

    TERMINATION_TRUNCATION_METRIC = ClosedPocketTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([
        InGoodsMenuSubGoal,
        SelectedCloseActionInMenuSubGoal,
        PointAtCoatSubGoal,
    ])

class DejaVuCloseWalletTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent closes the wallet.
    """

    TERMINATION_TRUNCATION_METRIC = ClosedWalletTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([
        InCoatPocketMenuSubGoal,
        SelectedCloseActionInMenuSubGoal,
        PointAtWalletSubGoal,
    ])

class DejaVuCheckedCoatTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent checks the coat.
    """

    TERMINATION_TRUNCATION_METRIC = CheckedCoatTerminationMetric
    SUBGOAL_METRIC = DummySubGoalMetric

class DejaVuCheckedGunTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent checks the gun.
    """

    TERMINATION_TRUNCATION_METRIC = CheckedGunTerminationMetric
    SUBGOAL_METRIC = DummySubGoalMetric

class DejaVuOpenSpigotTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent opens the spigot.
    """

    TERMINATION_TRUNCATION_METRIC = OpenSpigotTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([SelectedOpenActionInNormalSubGoal])

class DejaVuHitBottleTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent hits the bottle.
    """

    TERMINATION_TRUNCATION_METRIC = HitBottleTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([
        SelectedHitActionInNormalSubGoal,
        SockoOnScreenSubGoal,
    ])

class DejaVuEnterCellarTestTracker(DejaVuTestTracker):
    """
    A TestTracker for Deja Vu games that terminates when the agent enters the cellar.
    """

    TERMINATION_TRUNCATION_METRIC = EnterCellarTerminationMetric
    SUBGOAL_METRIC = make_subgoal_metric_class([OpenedCellarDoorOnScreenSubGoal])