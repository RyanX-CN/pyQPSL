from QPSLClass.Base import *


class QPSLVirtualStage:

    def __init__(self,
                 minimum: float = 0,
                 maximum: float = 100,
                 position: float = 10,
                 interval: int = 5) -> None:
        super().__init__()
        self.m_interval = interval
        self.m_minimum = minimum
        self.m_maximum = maximum
        self.m_per = (self.m_maximum - self.m_minimum) / 1000
        self.m_min_speed = self.m_per * (self.m_interval / 10)
        self.m_max_speed = self.m_per * (self.m_interval / 2)
        self.m_position = position
        self.m_target_position = position
        self.m_speed = 0
        self.m_acc = (self.m_max_speed -
                      self.m_min_speed) * self.m_interval / 1000
        self.m_mut = QMutex()
        self.m_state = False
        self.m_state_controller = SharedStateController(
            value=SharedStateController.State.Stop)

    def get_position(self):
        assert self.m_state
        return self.m_position

    def set_position(self, position: float):
        assert self.m_state
        self.m_position = position

    def get_minimum(self):
        assert self.m_state
        return self.m_minimum

    def get_maximum(self):
        assert self.m_state
        return self.m_maximum

    def get_range(self):
        assert self.m_state
        return self.m_minimum, self.m_maximum

    def get_state(self):
        return self.m_state

    def open(self):
        assert not self.m_state
        self.m_mut.lock()

        def run():
            while self.m_state_controller.is_continue():
                self.m_mut.lock()
                self.m_position += self.m_speed
                if self.m_position < self.m_target_position:
                    d = (self.m_target_position - self.m_position)
                    if d < self.m_per:
                        self.m_position = self.m_target_position
                        self.m_speed = 0
                    else:
                        if self.m_speed < self.m_min_speed:
                            self.m_speed = self.m_min_speed
                        else:
                            self.m_speed = min(self.m_max_speed,
                                               self.m_speed + self.m_acc)
                else:
                    d = (self.m_position - self.m_target_position)
                    if d < self.m_per:
                        self.m_position = self.m_target_position
                        self.m_speed = 0
                    else:
                        if self.m_speed > -self.m_min_speed:
                            self.m_speed = -self.m_min_speed
                        else:
                            self.m_speed = max(-self.m_max_speed,
                                               self.m_speed - self.m_acc)
                self.m_mut.unlock()
                sleep_for(self.m_interval)
            self.m_state = False
            self.m_state_controller.reply_if_stop()

        self.m_state = True
        self.m_state_controller.set_continue()
        QThreadPool.globalInstance().start(run)
        self.m_mut.unlock()

    def close(self):
        assert self.m_state
        self.m_mut.lock()
        self.m_state_controller.set_stop_until_reply()
        self.m_speed = 0
        self.m_mut.unlock()

    def is_opened(self):
        return self.m_state

    def home(self):
        self.m_mut.lock()
        self.m_target_position = 0
        self.m_mut.unlock()

    def move_to(self, target: float):
        assert self.m_state
        self.m_mut.lock()
        self.m_target_position = target
        self.m_mut.unlock()

    def stop_move(self):
        assert self.m_state
        self.m_mut.lock()
        self.m_target_position = self.m_position
        self.m_mut.unlock()

    def is_moving(self):
        assert self.m_state
        return self.m_position != self.m_target_position