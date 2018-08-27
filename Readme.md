# Email sender

This application helps to send a similar e-mail to many recipients at once.
Application can be found on https://easy-sending.herokuapp.com


## Usage

1. Enter login "guest" and password "321321" to enter.
2. Enter your gmail credentials (STARTTLS encrypted). Be sure that Less secure app in your Google account are allowed https://myaccount.google.com/lesssecureapps
3. If you want to have an example of message text and contacts file you can download them.
4. You can change everything except ${RECIPIENT_NAME} here the names of your recipients will be placed.
5. In contacts file it is necessary to place names in the first column and e-mails in the second. Also the file should contain a header.
6. Upload your files and press Submit button, e-mails are sent.


## Tools

- Python 3
- Flask
- MongoDB
- ReCaptcha
