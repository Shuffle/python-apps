# Base our app image off of the WALKOFF App SDK image
FROM frikky/shuffle:app_sdk as base

# We're going to stage away all of the bloat from the build tools so lets create a builder stage
FROM base as builder

# Install all alpine build tools needed for our pip installs
RUN apk --no-cache add --update alpine-sdk libffi libffi-dev musl-dev openssl-dev

# Install all of our pip packages in a single directory that we can copy to our base image later
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --prefix="/install" -r /requirements.txt

# Switch back to our base image and copy in all of our built packages and source code
FROM base
COPY --from=builder /install /usr/local
COPY src /app

# Install any binary dependencies needed in our final image
# RUN apk --no-cache add --update my_binary_dependency
RUN apk add --no-cache \
    ca-certificates \
    less \
    ncurses-terminfo-base \
    krb5-libs \
    libgcc \
    libintl \
    libssl1.1 \
    libstdc++ \
    tzdata \
    userspace-rcu \
    zlib \
    icu-libs \
    curl

RUN apk -X https://dl-cdn.alpinelinux.org/alpine/edge/main add --no-cache \
    lttng-ust

# Download the powershell '.tar.gz' archive
RUN curl -L https://github.com/PowerShell/PowerShell/releases/download/v7.1.4/powershell-7.1.4-linux-alpine-x64.tar.gz -o /tmp/powershell.tar.gz

# Create the target folder where powershell will be placed
RUN mkdir -p /opt/microsoft/powershell/7

# Expand powershell to the target folder
RUN tar zxf /tmp/powershell.tar.gz -C /opt/microsoft/powershell/7

# Set execute permissions
RUN chmod +x /opt/microsoft/powershell/7/pwsh

# Create the symbolic link that points to pwsh
RUN ln -s /opt/microsoft/powershell/7/pwsh /usr/bin/pwsh
RUN pwsh -Command Install-Module -Name ExchangeOnlineManagement -Force
RUN sh -c "yes | pwsh -Command 'Install-Module -Name PSWSMan'" 
RUN pwsh -Command 'Install-WSMan'
RUN pwsh -Command Import-Module 'Microsoft.PowerShell.Security' -Force

# Adds a replacement file which will be used to run the powershell script from python
COPY replacementfile.ps1 /app/replacementfile.ps1  
#COPY password.ps1 password.ps1  
#RUN pwsh -file password.ps1
#RUN pwsh -Command Get-Help Connect-IPPSSession
#RUN pwsh -Command Get-Help Connect-ExchangeOnline
#RUN pwsh -Command Get-Help New-PSSession 
#Connect-ExchangeOnline -CertificateFilePath "C:\Users\johndoe\Desktop\automation-cert.pfx" -CertificatePassword (ConvertTo-SecureString -String "<MyPassword>" -AsPlainText -Force) -AppID "36ee4c6c-0812-40a2-b820-b22ebd02bce3" -Organization "contosoelectronics.onmicrosoft.com"

COPY example.pfx /example.pfx
#RUN pwsh -Command 'Connect-ExchangeOnline -CertificateFilePath "./example.pfx" -CertificatePassword (ConvertTo-SecureString -String "<your password>" -AsPlainText -Force) -AppID "70a66541-50e6-47e4-83d9-ccaa55db7da9" -Organization "shufflertest2.onmicrosoft.com"'
#RUN pwsh -Command Get-QuarantineMessage -StartReceivedDate {time_from} -EndReceivedDate {time_to}
RUN pwsh -Command Get-EXOMailbox


# Finally, lets run our app!
WORKDIR /app
CMD python app.py --log-level DEBUG
