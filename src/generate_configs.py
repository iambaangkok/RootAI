from roottrainer.CSVOutputWriter import CSVOutputWriter

config_count = 0


def write_params(
        expand_count: int = 100,
        action_count_limit: int = 20,
        reward_func: str = "vp-difference",
        best_action_policy: str = "robust"):
    writer.write(["      expand-count: {}".format(expand_count)])
    writer.write(["      rollout-no: {}".format(1)])
    writer.write(["      action-count-limit: {}".format(action_count_limit)])
    writer.write(["      time-limit: {}".format(-1)])
    writer.write(["      reward-function: {}".format(reward_func)])
    writer.write(["      best-action-policy: {}".format(best_action_policy)])


NON_BASE_FACTIONS = ["ma", "ey"]
EXPAND_COUNTS = [50, 100, 200]
ACTION_COUNT_LIMITS = [20, 100, 200, -1]
REWARD_FUNCTIONS = ["win", "vp-difference", "vp-difference-relu"]
BEST_ACTION_POLICIES = ["max", "robust", "secure"]

writer: CSVOutputWriter = CSVOutputWriter("src/config/experiment")
for non_base_faction in NON_BASE_FACTIONS:
    for expand_count in EXPAND_COUNTS:
        for action_count_limit in ACTION_COUNT_LIMITS:
            for reward_func in REWARD_FUNCTIONS:
                for best_action_policy in BEST_ACTION_POLICIES:
                    config_file_name = "config-{}-{}.yml".format(config_count, non_base_faction)
                    writer.open(config_file_name)
                    writer.write(["""
screen:
  native-width: 1680
  native-height: 960
  width: 1280
  height: 720

logging:
  game:
    level: 50
  trainer:
    level: 50
  mcts:
    level: 50

simulation:
  command-line-mode:
    enable: true
  rendering:
    enable: true
  actions:
    rendering:
      enable: true
  f-key-action: random
  framerate: 60
  auto-next-round: true
  round: 100
  output:
    enable: true
    dir: output/experiment
  multiprocessing:
    enable: false
    core: 8

game:
  rendering:
    enable: true
  victory-point-limit: 30
  allow-dominance-card: false

agent:
  require-key-hold: false
  
  marquise:
    enable: true
    type: mcts
    mcts:
      type: mcts"""])
                    if non_base_faction is "ma":
                        write_params(
                            expand_count,
                            action_count_limit,
                            reward_func,
                            best_action_policy
                        )
                    else:
                        write_params()

                    writer.write(["""
  eyrie:
    enable: true
    type: mcts
    mcts:
      type: mcts"""])

                    if non_base_faction is "ey":
                        write_params(
                            expand_count,
                            action_count_limit,
                            reward_func,
                            best_action_policy
                        )
                    else:
                        write_params()

                    writer.close()
                    config_count += 1
