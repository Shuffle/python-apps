# GPG Tools
GPG tools is a utility app can help with encryption and decryption. It utilizes your private and public key, along with a password to do so, and requires a file as an input. 

## Authentication
Authentication for the app is necessary in order to decrypt or encrypt files or data. How this is handled from version 1.1.0 is through a Zip file with all your resources, uploaded to the Shuffle File storage. A prerequisite is already having a 

**Required Authentication Arguments:**
- File_ID: Points to the File ID of the Zip file containing your Private & Public key(s)
- Password: The password that protects your Private Key

Getting the ZIP's File ID:
1. Create your public & Private key
2. `zip -r gpg.zip .`
3. Upload
