from faker import Faker
from tempmail import EMail
import requests

def main() -> None:
    fake = Faker()
    email = EMail()
    print(f"Temporary email: {email.address}")
    print("Requesting free trial key")

    values = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "job_title": fake.job(),
        "institution": fake.company()
    }


    requests.get("https://www.maplesoft.com/contact/webforms/formprocessing/Process.aspx", params = {
        "email": email.address,
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
    }, allow_redirects = True)

    msg = email.wait_for_message()
    
    if body := msg.body:
        print("Got free trial url!")

        url = "https://www.maplesoft.com"

        pos = 0
        maple_len = len(url)

        while pos + maple_len < len(body):
            if body[pos : pos + maple_len] == url:
                pos += maple_len

                while body[pos] != '"' and pos + 1 < len(body) - 1:
                    url += body[pos]
                    pos += 1

                break

            pos += 1

        print(f"To activate your key, go to {url}")

        print("Inputted values are as follows:")
        
        for key, value in values.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()