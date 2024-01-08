# Manual MCTS Calculation

# Pseudocode
![Alt text](https://media.discordapp.net/attachments/740605851924168775/1193906124223696967/image.png?ex=65ae6ab9&is=659bf5b9&hm=c1204c7413f600ba0c4712aa9c5020db371091c2bcaa216fc2542c4945172997&=&format=webp&quality=lossless)

# Selection Phase

## Upper Bound Confidence Formula
![Alt text](https://cdn.discordapp.com/attachments/740605851924168775/1193903814609215488/image.png)
```
U_i(n)  = reward function of current player i
        = vp difference of current player i and the opponent o
        = vp_i - vp_o

N_i(n)  = number of tries
C = constant (there is theoretical argument that C should be √2)
PARENT(n) = parent of node n
```

## Our Code
```py
choices_weights = [
    (c.score / c.tries + c_param * np.sqrt(np.log(self.tries) / c.tries)) 
    for a, c in self.children
]
        
    return self.children[np.argmax(choices_weights)]
```

in this case,

```txt
U(n)    = c.score
N(n)    = c.tries
C       = c_param = 2 (default in textbook)
N(PARENT(n)) = self.tries
```

# Normal MCTS

## Observed State
- First turn of game starting with Eyrie player
- Picking which cards to insert in decree 

### MCT 1st iterations

```sh
INFO:child actions 10 
    [
        'Sappers (BIRD) to BUILD', 
        'Sappers (BIRD) to BATTLE', 
        'Sappers (BIRD) to MOVE', 
        'Sappers (BIRD) to RECRUIT', 
        'Dominance (Fox) (FOX) to BUILD', 
        'Dominance (Fox) (FOX) to BATTLE', 
        'Dominance (Fox) (FOX) to MOVE', 
        'Dominance (Fox) (FOX) to RECRUIT', 
        'Armorers (BIRD) to BUILD', 
        'Armorers (BIRD) to BATTLE'
    ]
INFO:choices_weights 
    [
        6.034854258770293, 
        -17.96514574122971, 
        -12.965145741229707, 
        21.03485425877029, 
        1.034854258770293, 
        0.03485425877029291, 
        -2.965145741229707, 
        9.034854258770293, 
        0.03485425877029291, 
        -9.965145741229707
    ]
INFO:params <score, tries> 
    [
        '<3, 1>', 
        '<-21, 1>', 
        '<-16, 1>', 
        '<18, 1>', 
        '<-2, 1>', 
        '<-3, 1>', 
        '<-6, 1>', 
        '<6, 1>', 
        '<-3, 1>', 
        '<-13, 1>', 
        '<-37, 10>' => self
    ]
INFO:best_action_sim Sappers (BIRD) to RECRUIT, best_action Sappers (BIRD) to RECRUIT
```

## Calculation
**Sappers (BIRD) to BUILD**
```txt
U(n)    = 3
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = 3 / 1 + 2 * sqrt(log(10) / 1)
        = 6.034854258770293
```

**Sappers (BIRD) to BATTLE**
```txt
U(n)    = -21
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = -21 / 1 + 2 * sqrt(log(10) / 1)
        = -17.96514574123
```

**Sappers (BIRD) to MOVE**
```txt
U(n)    = -16
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = -16 / 1 + 2 * sqrt(log(10) / 1)
        = -12.96514574123
```

**Sappers (BIRD) to RECRUIT**
```txt
U(n)    = 18
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = 18 / 1 + 2 * sqrt(log(10) / 1)
        = 21.03485425877
```

**Dominance (Fox) (FOX) to BUILD**
```txt
U(n)    = -2
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = -2 / 1 + 2 * sqrt(log(10) / 1)
        = 1.034854258770293
```

**Dominance (Fox) (FOX) to BATTLE**
```txt
U(n)    = -3
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = -3 / 1 + 2 * sqrt(log(10) / 1)
        = 0.03485425877029291
```

**Dominance (Fox) (FOX) to MOVE**
```txt
U(n)    = -6
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = -6 / 1 + 2 * sqrt(log(10) / 1)
        = -2.965
```
**Dominance (Fox) (FOX) to RECRUIT**
```txt
U(n)    = 6
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = 6 / 1 + 2 * sqrt(log(10) / 1)
        = 9.035
```
**Armorers (BIRD) to BUILD**
```txt
U(n)    = -3
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = -3 / 1 + 2 * sqrt(log(10) / 1)
        = 0.035
```
**Armorers (BIRD) to BATTLE**
```txt
U(n)    = -13
N(n)    = 1
C       = 2
N(PARENT(n)) = 10

UCBI    = -13 / 1 + 2 * sqrt(log(10) / 1)
        = -9.965
```
UCBI calculations are correct. Chosen node: Sappers (BIRD) to RECRUIT is also correct.

# One-Depth MCTS
They use the same UCTI formula.
## Logs 
```sh
INFO:child actions 3 ['COMMANDER', 'DESPOT', 'BUILDER']
INFO:choices_weights [-11.128116797812487, -6.728116797812486, -6.728116797812486]
INFO:params <score, tries> ['<-63, 5>', '<-41, 5>', '<-41, 5>', '<-145, 15>']
INFO:best_action_sim DESPOT, best_action DESPOT
```

Root
- <score, tries>
- (-145, 15)

Three child nodes:
- COMMANDER (-63, 5)
- DESPOT (-41, 5)
- BUILDER (-41, 5)

Chosen node: DESPOT (argmax chooses the first element that has max value)

## Calculation
**Commander**
```txt
U(n)    = -63
N(n)    = 5
C       = 2
N(PARENT(n)) = 15

UCBI    = -63 / 5 + 2 * sqrt(log(15) / 5)
        = -11.128
```
**DESPOT & BUILDER** (same params)
```txt
U(n)    = -41
N(n)    = 5
C       = 2
N(PARENT(n)) = 15

UCBI    = -41 / 5 + 2 * sqrt(log(15) / 5)
        = -6.728
```
UCBI calculations are correct. Chosen node: DESPOT is also correct.
# Conclusion
Our implementation of UCBI is correct.