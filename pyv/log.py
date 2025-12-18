import logging
import os


def getLogger(verbose=False, log_file="run.log"):
    """Get or configure the logger.

    Args:
        verbose (bool): If True, enable console logging and set to DEBUG level
        log_file (str): Path to log file

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger("pyv")

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set log level based on verbose mode
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    simple_formatter = logging.Formatter('%(levelname)-8s: %(message)s')

    # File handler - always log to file
    file_handler = logging.FileHandler(log_file, 'w')
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    logger.addHandler(file_handler)

    # Console handler - only if verbose
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.INFO)  # Only show INFO and above on console
        logger.addHandler(console_handler)

    return logger


# Default logger instance (disabled by default)
logger = getLogger(verbose=False)


def enable_logging(verbose=False, log_file="run.log"):
    """Enable and configure logging.

    Args:
        verbose (bool): If True, enable console output
        log_file (str): Path to log file
    """
    global logger
    logger = getLogger(verbose=verbose, log_file=log_file)
    return logger
