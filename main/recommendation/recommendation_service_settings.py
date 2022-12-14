from abc import abstractmethod


class RecommendationSettings:

    @abstractmethod
    def include(self) -> list:
        pass

    @abstractmethod
    def max_n(self) -> int:
        pass

    @abstractmethod
    def weights(self) -> dict:
        pass
