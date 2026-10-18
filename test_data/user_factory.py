import uuid

def create_user_data(user_type):
    user = {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "password": f"password_{uuid.uuid4()}",
        "type": user_type
    }

    if user_type == "BUSINESS":
        user["company_name"] = f"Company:{uuid.uuid4().hex[:8]}"

    return user