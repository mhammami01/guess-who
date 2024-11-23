class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, event, **kwargs):
        for observer in self._observers:
            observer.update(event, **kwargs)
