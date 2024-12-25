import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Créez un logger
    logger = logging.getLogger('flask_app')
    logger.setLevel(logging.DEBUG)  # Niveau de journalisation global

    # Gestionnaire de fichiers avec rotation
    file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    file_handler.setLevel(logging.INFO)  # Niveau pour le fichier
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Gestionnaire de console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Niveau pour la console
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Ajoutez les gestionnaires au logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
