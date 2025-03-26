import logging

# Configurar logging
logging.basicConfig(filename="bot.log", level=logging.INFO, format="[%(asctime)s] %(message)s")

def log_event(msg):
    print(msg)
    logging.info(msg)

def validate_payload(data):
    required_keys = ["symbol", "side", "qty", "leverage", "sl", "tp"]
    missing = [key for key in required_keys if key not in data]
    return missing
