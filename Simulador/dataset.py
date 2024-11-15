import json
from os import path
import pandas as pd

from utils import load_and_preprocess_transactions, get_initial_time, get_time_steps_count, apply_transactions

class Dataset:
    """
    Dataset
    """

    natural_tick_interval = 5 * 60

    datasets_dir_path = "datasets"
    initial_state_json_path = "initial_state.json"
    transactions_csv_path = "transactions.csv"

    transactions_previous_time_column = "previous_time"
    transactions_current_time_column = "current_time"
    transactions_nrc_column = "nrc"
    transactions_delta_enrolled_column = "delta_enrolled"
  
    def __init__(self, dataset_name):
        """
        Initialize the dataset
        """
        dataset_dir = path.join(self.datasets_dir_path, dataset_name)
        self._data = json.load(open(path.join(dataset_dir, self.initial_state_json_path)))
        self._transactions = load_and_preprocess_transactions(path.join(dataset_dir, self.transactions_csv_path), self.transactions_previous_time_column, self.transactions_current_time_column)
        self.initial_time = get_initial_time(self._transactions, self.transactions_previous_time_column, self.transactions_current_time_column)
        self.total_steps = get_time_steps_count(self._transactions, self.natural_tick_interval, self.transactions_previous_time_column, self.transactions_current_time_column)
        self.current_steps = 0
        self.updated_nrcs = 0

    def get(self):
        """
        Get the current data
        """
        return self._data
    
    def now(self):
        """
        Get the current time
        """
        return self.initial_time + pd.Timedelta(seconds=self.current_steps * self.natural_tick_interval)
    
    def tick(self):
        """
        Tick the dataset
        """
        if self.done():
            return
        self.current_steps += 1
        self.updated_nrcs += apply_transactions(
            self._data, 
            self._transactions, 
            self.now(), 
            self.transactions_current_time_column, 
            self.transactions_nrc_column, 
            self.transactions_delta_enrolled_column
        )

    def done(self):
        """
        Check if the simulation is done
        """
        return self.current_steps >= self.total_steps
