в# План переноса AIController

## Анализ текущей структуры

### Основные компоненты AIController:

1. **Главный метод**: `take_turn()` - выполняет весь ход AI
2. **Выбор цели**: 
   - `_select_target()` - выбор стратегической цели
   - `_select_roaming_target()` - случайная цель для исследования
   - `_find_priority_target()` - приоритетные цели (башни/телепорты)
   - `_needs_base_defense()` - проверка необходимости защиты базы
3. **Сбор кандидатов**:
   - `_collect_candidates()` - сбор всех возможных ходов
   - `_choose_candidate()` - выбор лучшего кандидата с учетом стратегии
4. **Применение хода**:
   - `_apply_move()` - изменение игрового состояния после хода
5. **Вспомогательные методы**:
   - `_is_blocking_enemy()` - проверка блокировки врага
   - `_is_defending_important()` - проверка защиты важных точек
   - `_distance()` - манхэттенское расстояние

### Legacy зависимости (что нужно заменить):

1. **Структуры данных**:
   - `factions: Sequence[dict]` → `list[Faction]`
   - `terrain: dict` → `World`
   - `Coord = Tuple[int, int]` → `Coord` (уже есть в v2)
   - `towers: List[Coord]` → `World._towers` (через методы World)
   - `portal_links: Optional[dict]` → `World.portal_links`
   - `me["base"]`, `me["territory"]` → `faction.base`, `faction.territory`

2. **Сервисы**:
   - `BuildService.can_build_at()` → `BuildValidator.validate()`
   - `BuildService.get_neighbors()` → `Coord.neighbors()`
   - `BuildService.is_source_active()` → `ReachabilityChecker` (через BuildValidator)
   - `VisibilityService.get_visible_cells()` → `VisibilityService.get_visible_cells()` (уже адаптирован)

3. **Константы**:
   - `cfg.FIELD_WIDTH`, `cfg.FIELD_HEIGHT` → нужно добавить в Settings или World
   - `cfg.TERRAIN_*` → `settings.terrain.*` или `TerrainType` enum

4. **Параметры режимов**:
   - `classic_mode: bool` → `GameModeFlags.classic`
   - `mountain_efficiency_mode: bool` → `GameModeFlags.mountain_efficiency`
   - `supply_mode: bool` → `GameModeFlags.supply`
   - `converted_mountains: Optional[set]` → остается как есть

## План переноса по этапам

### Этап 1: Базовая структура и зависимости
- [ ] Создать `src/ai/controller.py` с базовой структурой класса
- [ ] Заменить все `dict` на объекты (`Faction`, `World`, `Coord`)
- [ ] Заменить `BuildService` на `BuildValidator`
- [ ] Заменить `cfg` на `Settings` / `World` методы

### Этап 2: Методы выбора цели
- [ ] Перенести `_select_target()` - адаптировать под `Faction` объекты
- [ ] Перенести `_select_roaming_target()` - использовать `Coord.neighbors()`
- [ ] Перенести `_find_priority_target()` - использовать `World` методы
- [ ] Перенести `_needs_base_defense()` - адаптировать под новую структуру

### Этап 3: Сбор и выбор кандидатов
- [ ] Перенести `_collect_candidates()` - использовать `BuildValidator.validate()`
- [ ] Перенести `_choose_candidate()` - адаптировать под `BuildResult`
- [ ] Перенести вспомогательные методы (`_is_blocking_enemy`, `_is_defending_important`)

### Этап 4: Применение хода
- [ ] Перенести `_apply_move()` - **САМЫЙ СЛОЖНЫЙ** - нужно изменить состояние через объекты
- [ ] Заменить прямые изменения словарей на методы `Faction` и `World`
- [ ] Обработать захват базы, крепостей, башен, телепортов, мостов

### Этап 5: Главный метод
- [ ] Перенести `take_turn()` - объединить все части
- [ ] Адаптировать под новую архитектуру (убрать render_callback, wait_callback пока)
- [ ] Интегрировать с `VisibilityService`, `EventLog`, `BuildValidator`

### Этап 6: Рефакторинг и оптимизация
- [ ] Убрать дублирование кода
- [ ] Улучшить читаемость
- [ ] Добавить type hints
- [ ] Протестировать

## Ключевые изменения при переносе

### 1. Замена словарей на объекты:

**Legacy:**
```python
me = factions[faction_idx]
my_cells = me["territory"] | me["fortresses"] | {me["base"]}
```

**V2:**
```python
my_faction = factions[faction_idx]
my_cells = my_faction.all_buildings | {my_faction.base}
```

### 2. Замена BuildService на BuildValidator:

**Legacy:**
```python
allowed, cost, owner, is_fortress = BuildService.can_build_at(
    cell, me, factions, terrain, towers, portal_links,
    classic_mode, mountain_efficiency_mode, converted_mountains, supply_mode
)
```

**V2:**
```python
flags = GameModeFlags(
    classic=classic_mode,
    supply=supply_mode,
    mountain_efficiency=mountain_efficiency_mode
)
result = build_validator.validate(
    target_cell=cell,
    my_faction=my_faction,
    all_factions=factions,
    world=world,
    flags=flags,
    converted_mountains=converted_mountains
)
allowed = result.allowed
cost = result.cost
owner = result.owner
is_fortress = result.is_fortress
```

### 3. Замена terrain dict на World:

**Legacy:**
```python
is_water = terrain.get(cell) == cfg.TERRAIN_WATER
terrain[cell] = cfg.TERRAIN_BRIDGE
```

**V2:**
```python
is_water = world.is_water(cell)
world.build_bridge(cell)  # или world.set_terrain(cell, ...)
```

### 4. Замена применения хода:

**Legacy:**
```python
me["fortresses"].add(cell)
owner["territory"].remove(cell)
```

**V2:**
```python
my_faction.add_fortress(cell)
owner_faction.remove_territory(cell)
```

## Потенциальные проблемы

1. **Fortress ages** - в legacy есть `fortress_ages: Optional[dict]`, нужно решить, где это хранить в v2
2. **Render callbacks** - пока можно убрать или сделать опциональными
3. **Wait callbacks** - аналогично
4. **Captured towers** - нужно понять, где это хранить (возможно в GameState или отдельный сервис)

## Следующие шаги

1. Начать с Этапа 1 - создать базовую структуру
2. Постепенно переносить методы, тестируя каждый
3. После переноса всех методов - интегрировать с игровым циклом

