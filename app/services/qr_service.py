import hashlib

def generate_driver_qr_hash(franchise_number: str, name: str) -> str:
    """
    Creates a cryptographic hash of the driver's info. 
    The offline app verifies this to prevent colorum tricycles.
    """
    raw_data = f"{franchise_number}-{name}-MSUTCTO-LGU"
    return hashlib.sha256(raw_data.encode()).hexdigest()