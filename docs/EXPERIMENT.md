# Experiment
- Round count per experiment: 1000
## Configs
> Total permutations: 240 (+1 random = 241)
- Agents
  - Random (1)
  - MCTS
    - expand_count: 50, 100, 200, 400
    - [fixed] rollout_no: 1
    - action_count: 20, 100, 200, 400, -1
    - [fixed] time_limit: -1
    - reward_func: wins, vp-diff, vp-diff-relu
    - best_action_policy: max, robust, UCB, secure
## Method
- base (one-depth)

**Round 1**
- [M] 241 vs [E] base
- [M] base vs [E] 241

Take top 5 win_rate from each faction

**Round 2**
- [M] 5 vs [E] 5

Take top 1 from each faction

### Stats Per Round
- winner
- turn_count
- current_player
- vp_ma
- vp_ey

### Analysis
- win_rate
- avg_turn, avg_turn_ma_win, avg_turn_ey_win
- avg_ma_vp_ma_win, avg_ma_vp_ey_win
- avg_ma_vp_ey_win, avg_ma_vp_ma_win

