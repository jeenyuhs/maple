from faker import Faker
import requests
import time

def create_email():
    base_url = "https://api.mail.tm"
    response = requests.get(f"{base_url}/domains")
    response.raise_for_status()
    domains = response.json()["hydra:member"]
    domain = domains[0]["domain"]

    fake = Faker()
    email = fake.user_name() + "@" + domain
    password = fake.password(length=10)

    payload = {"address": email, "password": password}
    response = requests.post(f"{base_url}/accounts", json=payload)
    if response.status_code != 201:
        print("Error creating account:", response.json())
        raise Exception("Could not create mail.tm account")

 
    payload = {"address": email, "password": password}
    response = requests.post(f"{base_url}/token", json=payload)
    response.raise_for_status()
    token = response.json()["token"]

    return email, token

def get_email(token: str) -> dict:
    base_url = "https://api.mail.tm"
    headers = {"Authorization": f"Bearer {token}"}
    time.sleep(30) 
    while True:
        response = requests.get(f"{base_url}/messages", headers=headers)
        response.raise_for_status()
        data = response.json()
        if data["hydra:totalItems"] > 0:
            message_id = data["hydra:member"][0]["id"]
            response = requests.get(f"{base_url}/messages/{message_id}", headers=headers)
            response.raise_for_status()
            return response.json()
        time.sleep(5)

def main():
    fake = Faker()
    email, token = create_email()
    print(f"Temporary email: {email}")
    print("Requesting free trial key")
    print("Wait 30 seconds...")

    values = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "job_title": fake.job(),
        "institution": fake.company()
    }

    requests.get(
        "https://www.maplesoft.com/contact/webforms/formprocessing/Process.aspx",
        params={
            "email": email,
            "firstName": values["first_name"],
            "lastName": values["last_name"],
            "countryCode": "US",
            "comments": "",
            "segment": "Student",
            "title": values["job_title"],
            "company": values["institution"],
            "phone": "",
            "retURL": "https://www.maplesoft.com/contact/webforms/instant_eval_confirmation.aspx",
            "trackingCode": "TC-9648",
            "referrer": "https://www.maplesoft.com/products/maple/free-trial/index.aspx",
            "page_name": "Maple:Evaluation",
            "relatedProducts": "Maple"
        },
        allow_redirects=True
    )

    msg = get_email(token)

    body = msg.get("text") or msg.get("html")
    if body:
        print("Got free trial URL!")
        start_url = "https://www.maplesoft.com"
        pos = body.find(start_url)
        if pos != -1:
            end = body.find('"', pos)
            activation_url = body[pos:end] if end != -1 else body[pos:]
            print(f"To activate your key, go to {activation_url}")

        else:
            print("Activation URL not found in the email.")
            input("Press Enter to exit...") 
    else:
        print("Email body is empty or not found.")
        input("Press Enter to exit...") 

    print("Inputted values are as follows:")
    for key, value in values.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
    input("Press Enter to exit...") 

 