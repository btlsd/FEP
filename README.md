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

### Player Stats

Characters have five core attributes:

- **Strength**
- **Perception**
- **Endurance** – affects maximum health and energy as well as recovery rates
- **Charisma**
- **Intelligence**

These values influence activities like working and exploring.

### NPC Interactions

게임에는 개성 있는 여러 캐릭터가 존재합니다. 각 캐릭터는 호감도를
가지고 있으며 시간대에 따라 다른 장소에서 생활합니다. 플레이어는
동일한 장소에 있을 때 대화하거나 거래하고, 필요하면 돈을 빌리거나
전투를 벌일 수 있습니다.

### 캐릭터 정의

플레이어와 NPC에 대한 능력치와 스케줄, 성격 정보는 `characters.py`에
정리되어 있습니다. 새 캐릭터를 추가하거나 수정하고 싶다면 이 파일을
편집하면 됩니다.

### 장소

모든 장소 정의는 `locations.py`에 분리되어 있어 간단히 수정하거나
추가할 수 있습니다. 게임을 시작하면 "시스템 초기화" 메시지 후
인류연합국의 지하 거대한 하수도에서 눈을 뜨게 되며, 연결된 장소로
이동하며 탐험할 수 있습니다. `장소 이동` 옵션을 사용하여 현재 위치와
연결된 다른 지역으로 갈 수 있습니다.

일부 장소는 처음에는 보이지 않으며, 같은 장소에서 `탐험`을 수행하고
충분한 지각 능력을 갖추었을 때만 발견됩니다. 숨겨진 경로를 찾으면
해당 장소가 이동 목록에 추가됩니다.

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
새로운 물건을 넣을 수 없습니다. `행동` 메뉴에서 **소지품 확인**을 통해
현재 가지고 있는 물건과 무게를 살펴볼 수 있습니다.
