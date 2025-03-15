import logging

logger = logging.getLogger(__name__)    


logging.basicConfig(
        level=logging.ERROR,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')