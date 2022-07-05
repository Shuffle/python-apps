# This file is used to run powershell-remote commands from within Shuffle from python. 
# Fields using { } are to be replaced (username, password, command) 
Connect-IPPSSession -CertificateFilePath "./cert.pfx" -AppID "{APP_ID}" -Organization "{ORGANIZATION}" -CertificatePassword (ConvertTo-SecureString -String "{PASSWORD}" -AsPlainText -Force)

echo "SHFFL_START"
{COMMAND}
