
## :bulb: In this project we implemented a [DEMO](https://demo-pondersource-net.herokuapp.com) to represent the Trust UI of [peppol-php](https://github.com/pondersource/peppol-python).


### Try it by yourself 

Ιt is recommended to use use a virtual environment

```console
$ git clone https://github.com/pondersource/peppol-python-demo
$ cd peppol-python-demo
$ pip install -r requirements.txt
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```

## :wrench: How the [Demo](https://demo-pondersource-net.herokuapp.com) works

| Apps | Functionallity |
| --- | --- | 
| `accounts` | Handle the users who sign up |
| `app/main` | Main set up of the Django project |
| `contacts` | User's Contacts (collection of trusted WebIDs )|
| `content` | Most of the interface | 
| `messages` | How the messages ( XML files because we use a SOAP server) are sent |
| `quickbooks` | Quickbooks connection |
| `SOAP_client` | The SOAP client through which the messages/invoices will be sent|

* ## Contacts

### What a contact is?

Each Contact represents a trusted company or person, with whom you can exchange messages.

- [x] See your contacts 
- [x] Send contact requests
- [ ] See the requests you have sent
- [x] Receive contact requests ( Accept/Decline ) 
- [ ] Block a WebID from sending you messages
- [ ] Unblock a WebID 
- [x] Display notifications when you have a new message/contact request

* ## Accounts

### What an Account is?

Each account is a user who signed up at [pondersource Demo](https://demo-pondersource-net.herokuapp.com), and exists on our database.

- [x] Sign up ( WebID , username , email , password )
- [x] Log in/ Log out
- [x] Remind username
- [x] Resend activication code
- [x] Change password
- [x] Change username
- [x] Change email

* ## Messages

### What a Message is?

Each Message is a [XML](https://www.w3schools.com/xml/xml_whatis.asp) file.

- [x] Inbox
- [x] Outbox
- [x] Suppliers
- [x] Costumers
- [x] Compose a new message
- [x] Trash




