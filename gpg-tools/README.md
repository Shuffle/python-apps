# GPG Tools
GPG tools is a utility app can help with encryption and decryption of text and files. 
It requires your own GPG keystore containing private and public keys, along with the password to access the keystore. 

## Authentication
Authentication for the app is necessary in order to decrypt or encrypt files or data. 
How this is handled from version 1.1.0 is through a Zip file with all your resources, uploaded to the Shuffle File storage. 
The ZIP archive must contain the entire GnuPG Home Directory, named '.gnupg'

**Required Authentication Arguments:**
- Zip_File_ID: Points to the File ID of the Zip file containing your Private & Public key(s)
- Password: The password that protects your Private Key

Getting the ZIP's File ID:
1. Create your public & Private key with `gpg --full-gen-key`
2. A GPG Home Dir is created, under `~/.gnupg`
3. Compress the GPH Home Dir `zip -r gpg.zip .gnupg/`
4. Upload the ZIP file `gpg.zip` to Shuffle Files and obtain the FileID for the Zip file.