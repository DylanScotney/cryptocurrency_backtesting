
import abc

class dataLoadingStrat(metaclass=abc.ABCMeta):
    """
    Abstract base class for all data loading strategies
    Child classes include: webLoading, fileLoadingRaw, fileLoadingDF.
    """

    @abc.abstractmethod
    def get_data(self):
        """
        This method should get data via a given data loading strategy
        """