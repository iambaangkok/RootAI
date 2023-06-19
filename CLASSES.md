# Classes
- Logger (for logging events)

- Game
    - phases
        + birdsong()
        + daylight() 
        + evening()
- Board
    + List<Area> areas
    + 
- Area
    + List<Clearing> connected_clearing
    + List<Forest> connected_forest
    - Clearing
        + suit: {FOX, RABBIT, MOUSE}
        + List<Slot> slots
        + Map<Token, Int> token_count
        + Map<Warrior, Int> warrior_count
        + get_ruler()
    - Forest
        + bool exists_vagabond
- Slot
    + Building building
Building
    + type: {EMPTY, RUIN, SAWMILL, WORKSHOP, RECRUITER, ROOST, BASE}
- Warrior
    + faction: {Marquise, Decree, Alliance, Vagabond}

- Faction
    + victory_point
    + List<Card> effects
    + List<Card> hand
    
    - Marquise
        + Map<Building, Map<Int , Function>> BUILDING_PLACE_ACTION?
        + Map<Building, Int> building_tracker
        + place(Building):
            <!-- place building -->
            <!-- execute BUILDING_PLACE_ACTION(building_tracker[b]) -->
    - EyrieDynasties
        - EyrieLeader
            + name: {Commander, Despot, Builder, Charismatic}
            + viziers: {[MOVE,BATTLE],[MOVE,BUILD],[RECRUIT,MOVE],[RECRUIT,BATTLE]}
            + Bool is_face_down:
        - LoyalVizier 
        + String DECREE: {RECRUIT, MOVE, BATTLE, BUILD}
        + Map<String, List<Card>> decree_slots:  
        + List<Function> ROOST_RESOLVE_EVENTS
        + Int roost_tracker (at which position, 0 = no roosts placed)
        <!-- Setup -->
        + setup()
            + gather_warriors()
            + place_starting_roost_and_warriors()
            + choose_leader()
            + tuck_viziers()
            + fill_roosts_track()
        <!-- Birdsong  -->
        + draw_card() <!-- case: no cards in hand -->
        + add_card_to_decree(Card, DecreeSlot) <!-- can be done up to 2 times  -->
        + a_new_roost()
        + a_new_roost(Clearing) <!-- case: multiple fewest warriors clearings  -->
        <!-- Daylight -->
        + craft()
        + resolve_decrees()
            <!-- Recruit -->
            + do while possible: <!--else fall into turmoil-->
                + get_recruitable_card_clearings(): List<Pair<Card, Clearing>>
                + recruit(Card)
            <!-- Move -->
            + do while possible: <!--else fall into turmoil-->
                + get_max_movable_warrior_clearing_from_tos(): List<Pair<Card, Clearing from, Clearing to, Int warrior_count>>
                + move(Card, Clearing, Clearing, Int)
            <!-- Battle -->
            + do while possible: <!--else fall into turmoil-->
                + get_battleable_clearings(): List<Pair<Card, Clearing>>
                + battle(Card, Clearing)
            <!-- Build -->
            + do while possible: <!--else fall into turmoil-->
                + get_buildable_clearings(): List<Clearing>
                + build(Clearing)
        <!-- Turmoil -->
        + fall_into_turmoil()
            + humiliate()
            + purge()
            + depose()
        <!-- Evening -->
        + score_points
    - Alliance
        + Map<Int, Function> baseTracker
        + Map<Int, Pair<Int, Function>> sympathyTracker 
            <!-- Map<trackId> -->
        + List<Card> supporters
        + officers
        + revolt()
        + spread_sympathy()
    - Vagabond
        + Map<Int, Function>

- Card
    + req_craft
    + effect()
    + List<Item> items
- Item