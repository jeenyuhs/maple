from faker import Faker
import requests
import time

def create_mailtm_account():
    base_url = "https://api.mail.tm"
    # Get an available domain
    response = requests.get(f"{base_url}/domains")
    response.raise_for_status()
    domains = response.json()["hydra:member"]
    domain = domains[0]["domain"]
    
    fake = Faker()
    email = fake.user_name() + "@" + domain
    password = fake.password(length=10)
    
    # Create a new account
    payload = {"address": email, "password": password}
    response = requests.post(f"{base_url}/accounts", json=payload)
    if response.status_code != 201:
        print("Error creating account:", response.json())
        raise Exception("Could not create mail.tm account")
    
    # Log in to retrieve a token
    payload = {"address": email, "password": password}
    response = requests.post(f"{base_url}/token", json=payload)
    response.raise_for_status()
    token = response.json()["token"]
    
    return email, token

def get_newest_email(token: str) -> dict:
    base_url = "https://api.mail.tm"
    headers = {"Authorization": f"Bearer {token}"}
    time.sleep(60)  # Wait for 60 seconds before fetching emails
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
    # Create a temporary mail.tm account and retrieve the access token
    email, token = create_mailtm_account()
    print(f"Temporary email: {email}")
    print("Requesting free trial key")

    values = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "job_title": fake.job(),
        "institution": fake.company()
    }

    # Submit the free trial request using the temporary email
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

    # Wait for the email to arrive and then fetch it
    msg = get_newest_email(token)
    
    # Try to extract the free trial URL from the email content
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
    else:
        print("Email body is empty or not found.")
    
    print("Inputted values are as follows:")
    for key, value in values.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
