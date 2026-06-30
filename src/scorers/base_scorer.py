from abc import ABC, abstractmethod

class BaseScorer(ABC):
    """
    Base class for all scoring modules.
    """

    @abstractmethod
    def score(self, candidate, job, features=None):
        raise NotImplementedError