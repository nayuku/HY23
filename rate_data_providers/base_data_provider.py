from abc import ABC, abstractmethod
from decimal import Decimal


class BaseDataProvider(ABC):
    def __init__(self, **kwargs):
        self.client = kwargs.get('client')

    @property
    @abstractmethod
    def source_name(self) -> str:
        raise Exception('DataProvider must override the "source_name" property.')

    @abstractmethod
    def get_rate_value(self, crypto, currency) -> Decimal:
        raise Exception('DataProvider must override the "get_trade" method.')


def get_source_names():
    source_names = sorted([str(cls.source_name).upper() for cls in BaseDataProvider.__subclasses__()])
    return source_names


def get_data_provider(source_name):
    if source_name.upper() not in get_source_names():
        raise Exception(f"The specified source: '{source_name}' is not supported.")
    return [data_provider() for data_provider in BaseDataProvider.__subclasses__() if
            str(data_provider.source_name).upper() == source_name.upper()][0]
