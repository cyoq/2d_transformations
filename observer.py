class Observer:

    def register_observer(self, observable: "Observable"):
        observable.register_observer(self)

    def notify(self):
        pass


class Observable:

    def __init__(self):
        self._observer = None

    def register_observer(self, observer: Observer):
        self._observer = observer

    def notify_observers(self):
        self._observer.notify()
