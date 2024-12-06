import logging
import pandas as pd
import builtins

# Configuración global del logger
logger = logging.getLogger('global_logger')
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler('do_scrap.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(console_handler)

# Override the print function
original_print = builtins.print

def custom_print(*args, **kwargs):
    for arg in args:
        if isinstance(arg, pd.DataFrame):
            # Log the DataFrame to the file
            logger.debug("\n" + arg.to_string())
        else:
            # Use the original print for non-DataFrame objects
            original_print(arg, **kwargs)

# Replace the built-in print with the custom print
builtins.print = custom_print
