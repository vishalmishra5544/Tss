# Use the official .NET SDK 6 image as a build environment
#FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
#FROM mcr.microsoft.com/windows/servercore:ltsc2019 AS base
FROM mcr.microsoft.com/windows/servercore:ltsc2022-amd64 as base
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

## Install .net
RUN Invoke-WebRequest -OutFile dotnet-sdk-6.0.102-win.exe https://download.visualstudio.microsoft.com/download/pr/fb14ba65-a9c9-49ce-9106-d0388b35ae1b/7bbfe92fb68e0c9330c9106b5c55869d/dotnet-sdk-6.0.102-win-x64.exe; \
    Start-Process "dotnet-sdk-6.0.102-win.exe" -ArgumentList "/passive" -wait -Passthru; \
    Remove-Item -Force dotnet-sdk-6.0.102-win.exe

# Set the working directory
WORKDIR /app
EXPOSE 8000

# Change the base image to a Windows Server Core image

# Use the Windows image as the base for the build stage
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /TrackWizzService
COPY [".", "."]
RUN dotnet restore "TrackWizz.Core.ServiceLib/CoreServiceLib/CoreServiceLib.csproj" 
RUN dotnet restore "TrackWizz.Service.CKYCSearchDownload/CKYCSearchDownloadService/CKYCSearchDownloadService.csproj" 
COPY . .
WORKDIR "/TrackWizzService/TrackWizz.Core.ServiceLib/CoreServiceLib/"
RUN dotnet build "CoreServiceLib.csproj" -c Release -o /app/build
WORKDIR "/TrackWizzService/TrackWizz.Service.CKYCSearchDownload/CKYCSearchDownloadService/"
RUN dotnet build "CKYCSearchDownloadService.csproj" -c Release -o /app/build

# Continue with the rest of your Dockerfile
FROM build AS publish
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "TrackWizz.Service.CKYCSearchDownloadService.dll", "--urls", "http://0.0.0.0:8000"]
