from abc import abstractmethod, ABC


class LocationRestriction(ABC):
    @abstractmethod
    def check(self, location: str, target_location: str) -> bool:
        raise NotImplementedError()


class Anywhere(LocationRestriction):
    def check(self, location: str, target_location: str) -> bool:
        return True


class SelfOnly(LocationRestriction):
    def check(self, location: str, target_location: str) -> bool:
        return location == target_location


class SelfParent(LocationRestriction):
    def check(self, location: str, target_location: str) -> bool:
        return target_location.startswith(location)


class SelfParentSibling(LocationRestriction):
    def check(self, location: str, target_location: str) -> bool:
        return target_location.startswith(location) or \
               ("." in location and "." in target_location and
                location.rsplit(".", maxsplit=1) == target_location.rsplit(".", maxsplit=1))