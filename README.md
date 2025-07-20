# FEP

FEP stands for "Far East Project." This repository contains a simple text-based
life simulation game set in a far-future Seoul and beyond. All in-game text is in Korean.

## Running the Game

```bash
python game.py
```


During the game you will be prompted in Korean to choose among four main categories:

1. **이동** – 장소나 국가를 바꿉니다.
2. **NPC 선택** – 같은 장소에 있는 인물과 상호작용합니다.
3. **행동** – 일하기, 식사, 잠자기, 탐험 등의 활동을 수행합니다.
4. **메뉴** – 게임 종료 등 기타 기능을 선택합니다.

이 세계에는 네 개의 주요 국가가 존재합니다: **인류연합국**, **거합**, **탐랑**, 그리고 **전계국**입니다. 거합은 인간이 동식물에게 가한 실험으로 지능을 얻은 존재들이 모여 만든 나라이고, 탐랑은 개성을 중시해 오프라인으로 방랑하는 기계들의 느슨한 모임입니다. 전계국은 이들을 고장난 집단으로 여기며 모든 기계를 하나로 묶으려 합니다.

각 국가는 고유한 화폐 단위를 사용합니다. 인류연합국의 **연화**, 거합의 **거합권**, 탐랑의 **탐랑칩**, 전계국의 **전계 데이터**가 그것입니다. 전계국은 특히 실물 화폐보다 데이터를 통한 거래를 선호하며 다른 국가의 화폐를 받으면 수수료가 붙습니다.

### Player Stats

Characters have six core attributes:

- **Strength**
- **Perception**
- **Endurance** – affects maximum health and 기력 as well as recovery rates
- **Charisma**
- **Intelligence**
- **Agility** – higher agility lets your turn gauge fill faster in battle

These values influence activities like working and exploring. From these base attributes the game derives secondary stats used in daily life:

- **포만감** – how full you are, decreases with time and activities
- **기력** – stamina for actions, mainly restored by sleeping
- **청결도** – gets lower over time or when exploring, restored by washing

The maximum values and recovery rates of these secondary stats scale with the primary attributes such as Endurance or Charisma.

### NPC Interactions

게임에는 개성 있는 여러 캐릭터가 존재합니다. 각 캐릭터는 호감도를
가지고 있으며 시간대에 따라 다른 장소에서 생활합니다. 플레이어는
동일한 장소에 있을 때 대화하거나 거래하고, 필요하면 돈을 빌리거나
전투를 벌일 수 있습니다.
상인 NPC는 보통 키오스크를 통해 거래하지만, 낙후된 지역에서는
직접 대화로 현금이나 물건을 주고받는 방식의 거래가 이루어집니다.
이때 구입 가능한 품목과 가격은 `characters.json`의 `shop` 항목으로
관리됩니다.

### 캐릭터 정의

플레이어와 NPC에 대한 능력치와 스케줄, 성격 정보는 `data/characters.json`
파일에 기록되어 있으며 로딩 시 `characters.py`가 이를 읽어 들입니다.
JSON 형식이라 새로운 NPC를 손쉽게 추가하거나 수정할 수 있습니다.

각 NPC는 성격(Big Five OCEAN 지표), 나이, 성별, 직업, 지위, 출신 국가 등 다
양한 속성을 지니며, 인사말 역시 이러한 정보를 조합해 생성됩니다. 
`data/dialogues.json`에는 성별, 나이대, 직업, 출신 국가, 지위별 문구는 물론
Big Five 다섯 항목의 높고 낮음을 조합한 32가지 성격 유형별 대사가 준비돼
있습니다. `dialogues.py`가 이를 읽어 NPC 특성에 맞는 인사말을 만들어 줍니다.

### 장소

모든 장소와 국가 정보는 `data/locations.json`에 정의되어 있으며
`locations.py`에서 읽어 들여 객체로 변환합니다. 게임을 시작하면 "시스템 초기화" 메시지 후
인류연합국의 지하 거대한 하수도에서 눈을 뜨게 되며, 연결된 장소로
이동하며 탐험할 수 있습니다. `장소 이동` 옵션을 사용하여 현재 위치와
연결된 다른 지역으로 갈 수 있습니다.

일부 장소는 처음에는 보이지 않으며, 같은 장소에서 `탐험`을 수행하고
충분한 지각 능력을 갖추었을 때만 발견됩니다. 숨겨진 경로를 찾으면
해당 장소가 이동 목록에 추가됩니다.

각 장소는 시간대에 따라 분위기가 달라지며, 특정 시간에만 출입이 가능할
수 있습니다. 게임의 하루는 24시간제를 4시간 단위로 나눈 여섯 구간
(새벽, 아침, 오전, 오후, 저녁, 밤)으로 표현됩니다. 예를 들어 중앙 시장은
아침부터 저녁까지만 열리고, 비밀 실험실은 밤에만 들어갈 수 있습니다.
`gui.py`는 현재 시간에 맞는 장소 묘사를 보여 줍니다.

### GUI

`gui.py`는 플레이어의 상태와 현재 위치 정보를 보기 좋게 출력해 주는
간단한 텍스트 인터페이스를 제공합니다. 화면의 상단에는 건강 상태와
기본 스탯이 표시되고, 구분선 아래에는 장소 묘사와 주변 인물 목록,
또 다른 구분선 아래에는 이동 가능한 다른 장소가 나열됩니다.

### 인벤토리

플레이어는 장비에 따라 들 수 있는 물건의 무게가 결정됩니다. 기본 용량은
5이고, 주머니가 달린 옷이나 가방을 장비하면 추가 용량이 늘어납니다.
가방 종류에 따라 추가 용량이 다르며, 여행용 캐리어나 카트를 사용하면
훨씬 많은 물건을 운반할 수 있습니다. 카트의 경우 크기에 따라 건물 내부로
들어갈 수 있는지 여부가 달라집니다(대형 카트는 실내 진입이 어렵습니다).
아이템마다 무게가 정해져 있어 현재 들고 있는 총 무게가 용량을 초과하면
새로운 물건을 넣을 수 없습니다. `행동` 메뉴에서 **소지품 확인**이나
**씻기** 등을 선택해 일상적인 관리도 할 수 있습니다.
아이템 정보는 `data/items.json`에 정리되어 있어 무게나 이름을 손쉽게
수정하거나 새로운 아이템을 추가할 수 있습니다.

지각(**Perception**) 수치가 낮으면 무게와 부피를 정확히 파악하기 어렵기
때문에, 소지품 목록과 상태 창에 표시되는 수치는 오차가 생길 수 있습니다.
지각이 높을수록 이러한 오차 범위가 줄어들어 실제 값과 거의 같게 보입니다.

### 신체 개조와 장비

`equipment.py`에는 가방 같은 장비와 신체 개조 모듈이 정의되어 있습니다.
플레이어는 특정 부위에 사이버네틱 개조를 장착해 능력치를 올릴 수 있으며,
게임 내에서 **신체 개조** 행동을 통해 원하는 모듈을 설치할 수 있습니다.
모드마다 설치를 위한 전용 부품이 존재하므로 인벤토리에 해당 부품을
소지하고 있어야 시술이 가능합니다.
신체 개조는 대체로 전문 상점에서 진행되며, 이런 상점들은 대개 데이터 송수신
으로 의뢰와 결제를 처리합니다. 도시 외곽이나 슬럼가 등 낙후된 지역에서는
불법 시술이 성행하기도 하는데, 이 경우 시술 실패나 가품 부품 사용 위험이
있습니다. 반대로 고급화된 도심의 합법 상점에서는 이런 위험이 거의 없습니다.
눈 개조의 경우 여러 기업이 서로 다른 기능을 제공합니다. 예를 들어
"아이리움"사의 적외선 강화 눈은 투명화된 생물을 감지할 수 있고,
"정밀전자"의 분석용 눈은 정확한 타격 확률을 높여 주지만 고성능
기능을 사용하려면 추가로 뇌 인터페이스 모듈을 장착해야 합니다. 왼쪽과
오른쪽 눈을 각각 다르게 개조하는 것도 가능합니다.
장착된 개조는 상태 창에서 확인할 수 있습니다.

### 전투

NPC와 싸우게 되면 전투는 턴제로 진행됩니다. 각 참여자는 "턴 게이지"
가 0이 될 때마다 차례가 돌아옵니다. 민첩(**Agility**) 수치가 높을수록
턴 게이지가 더 빨리 소모되어 보다 자주 행동할 수 있습니다. 전투 로직은
`battle.py`에 구현되어 있습니다.
