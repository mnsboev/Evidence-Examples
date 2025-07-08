FROM mcr.microsoft.com/windows/servercore:ltsc2022

WORKDIR C:\\app

RUN powershell -Command \
    Set-ExecutionPolicy Bypass -Scope Process -Force; \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; \
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

RUN choco install nodejs -y

RUN refreshenv

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run package

EXPOSE 8080

CMD ["node", "C:\\app\\server.js"] 