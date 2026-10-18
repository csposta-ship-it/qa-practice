
SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "access_token",
    "refresh_token",
    "authorization",
    "client_secret",
}


def mask_sensitive_data(data):
    if isinstance(data, dict):
        masked_data = {}

        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                masked_data[key] = "********"
            else:
                masked_data[key] = mask_sensitive_data(value)

        return masked_data

    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]

    return data
