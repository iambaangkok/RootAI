# State Complexity

Board
- 12 Areas 
    - buildings [1, 2, 2, 1, 2, 1, 2, 1 ,2 ,2, 1] = 16 
        - 5 building types
            - 7 roosts = placable 16+7 not placed = (23 C 7) = 
            - 6 sawmills, recruiter, workshop
                - each = placable 16+5 not placed = (21 C 6) = 
            - = (23 C 7) x (21 C 6)
            - = 245157 x 54264
            - = 13303199448
            - = 1.33 x 10^10 states
- Item supply
    - 12 Items supply on board (uncrafted/crafted)
        - [ref: Items in Games Without Vagabonds](https://boardgamegeek.com/thread/2034705/items-games-without-vagabonds)
        - = ~2^12 states = 4096 states
- Warriors
    - Marquis: 25
    - Decree: 30
    - = 13^55 states = 2 x 10^61 states

- Cards
    - 54 cards
        - duplicate [2, 2, 2, 2, 3 ,2, 2, 2, 2, 2, 2] multiply all = 3072
        - 42 distinct cards
        - [ref: Cards List](#cards-list)
    - deck (1)
    - hand (1)
        - whose hand (2)
        - no limit but need to discard down to 5 at turn end
        - [ref: Hand Size Question](https://boardgamegeek.com/thread/2051125/hand-size-question)
    - discarded (1)
    - Decree slot (4)
    - = 8 ^ 54 states = 6 x 10^48 states 
    - reduced states = 8^54 / 3072 = 2 x 10^45

- Faction Specific
    - Distinct Eyrie Leader 4
        - = 4 x 3 x 2 x 1
        - = 24
    - Loyal Vizier 2

- Victory Points
    - 30 x 30 

### Total states
- = 1.33 x 10^10 x 4096 x 2 x 10^61 x 2 x 10^45 x 24
- = **5.23 x 10^121**

### Cards List

- Ambush (Bird) 2
- Birdy Handle (Bird) 1
- Armorers (Bird) 2
- Woodland Runners (Bird) 1
- Arms Trader (Bird) 1
- Crossbow (Bird) 1
- Sappers (Bird) 2
- Brutal Tactics (Bird) 2
- Royal Claim (Bird) 1
- total = 13 (duplicate 2 2 2 2)

- Ambush (Fox) 1   
- Gently Used Knapsack (Fox) 1  
- Root Tea (Fox) 1   
- Travel Gear (Fox) 1    
- Protection Racket (Fox) 1   
- Foxfolk Steel (Fox) 1
- Anvil (Fox) 1
- Stand and Deliver! (Fox) 2
- Tax Collector (Fox) 3
- Favor of the Foxes (Fox) 1
- total = 13 (duplicate 3 2)

- Ambush (Rabbit) 1
- Smuggler's Trail (Rabbit) 1
- Root Tea (Rabbit) 1
- A Visit to Friends (Rabbit) 1
- Bake Sale (Rabbit) 1
- Command Warren (Rabbit) 2
- Better Burrow Bank (Rabbit) 2
- Cobbler (Rabbit) 2
- Favor of the Rabbits (Rabbit) 1
- total = 12 (duplicate 2 2 2)

- Ambush (Mouse) 1
- Mouse-in-a-Sack (Mouse) 1
- Root Tea (Mouse) 1
- Travel Gear (Mouse) 1
- Investments (Mouse) 1
- Sword (Mouse) 1
- Crossbow (Mouse) 1
- Scouting Party (Mouse) 2
- Codebreakers (Mouse) 2
- Favor of the Mice (Mouse) 1
- total = 12 (duplicate 2 2)

- Distinct Dominance 4

