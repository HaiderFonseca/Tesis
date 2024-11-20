import time
from datetime import datetime
from reactivex.scheduler import EventLoopScheduler

from dataset import Dataset

class State:
    """
    State of the server
    """

    _data = None
    _scheduler = None
    default_dataset_name = "Empty"

    def __init__(self):
        """
        Initialize the state
        """
        self.restart(self.default_dataset_name, 0)

    def restart(self, dataset_name, tick_interval):
        """
        Restart the server
        """

        # Init state metadata
        self.last_restart = time.time()
        self.dataset_name = dataset_name
        self.tick_interval = tick_interval
        self.change_on_demand = (tick_interval == 0)

        # Init dataset
        if self._data:
            del self._data
        self._data = Dataset(dataset_name)
        
        # Init virtual time scheduler if needed
        if self._scheduler:
            self._scheduler.dispose()
        if not self.change_on_demand:
            self._scheduler = EventLoopScheduler()
            self._scheduler.schedule_periodic(self.tick_interval, lambda _: self._data.tick())
        else:
            self._scheduler = None

    def get_data(self):
        """
        Get the current data
        """
        if self.change_on_demand:
            self._data.tick()
        return self._data.get()
    
    def is_done(self):
        """
        Check if the simulation is done
        """
        return self._data.done()
    
    def get_dataset_metadata(self):
        """
        Get the dataset metadata
        """
        return {
            "initial_time": self._data.initial_time,
            "current_time": self._data.now(),
            "current_steps": self._data.current_steps,
            "total_steps": self._data.total_steps,
            "updated_nrcs": self._data.updated_nrcs,
        }
