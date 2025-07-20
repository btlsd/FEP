class Nation:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Location:
    def __init__(self, name, description, nation):
        self.name = name
        self.description = description
        self.nation = nation
        self.connections = []  # list of other Location objects

    def connect(self, other):
        if other not in self.connections:
            self.connections.append(other)
        if self not in other.connections:
            other.connections.append(self)


# Nations
NATIONS = [
    Nation("휴먼 프론티어", "인간 위주의 국가"),
    Nation("자연 연합", "여러 종들이 의견을 모아 운영하는 생태계 중심의 국가"),
    Nation("오프라인 기계 국가", "개체가 오프라인 상태로 존재하는 기계들의 국가"),
    Nation("온라인 기계 네트워크", "개체가 온라인 상태로 연결된 기계 국가"),
]

# Locations for the human nation
SEWER = Location(
    "거대한 하수도",
    "휴먼 프론티어 수도 지하를 흐르는 광대한 하수도",
    NATIONS[0],
)
STATION = Location(
    "지하 정거장",
    "도시 각지로 통하는 낡은 정거장",
    NATIONS[0],
)
MARKET = Location(
    "중앙 시장",
    "사람들로 붐비는 시장 거리",
    NATIONS[0],
)
RESIDENTIAL = Location(
    "주거 지구",
    "평범한 주거 지역",
    NATIONS[0],
)

# Connect locations
SEWER.connect(STATION)
STATION.connect(MARKET)
STATION.connect(RESIDENTIAL)

# Default locations for each nation when first arrived
DEFAULT_LOCATION_BY_NATION = {
    NATIONS[0]: SEWER,
    NATIONS[1]: Location("연합 수도", "자연 연합의 중심 도시", NATIONS[1]),
    NATIONS[2]: Location("기계 도시", "오프라인 기계들의 집합", NATIONS[2]),
    NATIONS[3]: Location("디지털 허브", "온라인 기계들의 중심", NATIONS[3]),
}

# List of all locations (including generated defaults)
LOCATIONS = [
    SEWER,
    STATION,
    MARKET,
    RESIDENTIAL,
    *DEFAULT_LOCATION_BY_NATION.values(),
]
