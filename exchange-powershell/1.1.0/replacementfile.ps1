# This file is used to run powershell-remote commands from within Shuffle from python. 
# Fields using { } are to be replaced (username, password, command) 
Connect-ExchangeOnline -CertificateFilePath "./cert.pfx" -AppID "{APP_ID}" -Organization "{ORGANIZATION}" -CertificatePassword (ConvertTo-SecureString -String "{PASSWORD}" -AsPlainText -Force)

echo "ANYTHING BEFORE THIS LINE IS NOT A PART OF THE RESULT AND SHOULD BE IGNORED. IF YOU SEE THIS TEXT IT IS PROBABLY DUE TO GETTING NO RESULTS"
{COMMAND}
