import logging

from src.roottrainer.RootTrainer import RootTrainer

logging.basicConfig(level=logging.NOTSET)
LOGGER = logging.getLogger('LOGGER')

trainer = RootTrainer()
trainer.run()
