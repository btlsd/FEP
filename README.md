# FEP

FEP stands for "Far East Project." This repository contains a simple text-based
life simulation game set in a far-future Seoul and beyond. All in-game text is in Korean.

## Running the Game

```bash
python game.py
```

During the game you will be prompted in Korean to choose actions such as working, eating, sleeping, exploring, or traveling between nations. The world contains several distinct countries: a human-focused nation, a large ecological federation of many species, an offline machine state, and an online machine network. Manage your character's stats and survive as long as possible while visiting these places.

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
휴먼 프론티어의 지하 거대한 하수도에서 눈을 뜨게 되며, 연결된 장소로
이동하며 탐험할 수 있습니다. `장소 이동` 옵션을 사용하여 현재 위치와
연결된 다른 지역으로 갈 수 있습니다.

### GUI

`gui.py`는 플레이어의 상태와 현재 위치 정보를 보기 좋게 출력해 주는
간단한 텍스트 인터페이스를 제공합니다. 화면의 상단에는 건강 상태와
기본 스탯이 표시되고, 구분선 아래에는 장소 묘사와 주변 인물 목록,
또 다른 구분선 아래에는 이동 가능한 다른 장소가 나열됩니다.
