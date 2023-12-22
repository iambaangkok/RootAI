import logging

from src.roottrainer.RootTrainer import RootTrainer

logging.basicConfig(level=logging.NOTSET)
logging.getLogger('game_logger').setLevel(logging.INFO)
logging.getLogger('trainer_logger').setLevel(logging.INFO)
logging.getLogger('mcts_logger').setLevel(logging.INFO)

trainer = RootTrainer()
trainer.run()
