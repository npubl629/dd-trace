# Stage 1: Build the application
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy the project files and restore any dependencies
COPY ["FastTimer.csproj", "./"]
RUN dotnet restore "./FastTimer.csproj"

# Copy the rest of the application files
COPY . .

# Build the application
RUN dotnet build "FastTimer.csproj" -c Release -o /app/build

# Publish the application
RUN dotnet publish "FastTimer.csproj" -c Release -o /app/publish

# Stage 2: Run the application
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Copy the published files from the build stage
COPY --from=build /app/publish .

# Expose port 80
EXPOSE 80

# Set the entrypoint
ENTRYPOINT ["dotnet", "FastTimer.dll"]