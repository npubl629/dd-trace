# Stage 1: Build the application
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy the project files and restore any dependencies
COPY ["Metrics.Idle.csproj", "./"]
RUN dotnet restore "./Metrics.Idle.csproj"

# Copy the rest of the application files
COPY . .

# Build the application
RUN dotnet build "Metrics.Idle.csproj" -c Release -o /app/build

# Publish the application
RUN dotnet publish "Metrics.Idle.csproj" -c Release -o /app/publish

# Stage 2: Run the application
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Copy the published files from the build stage
COPY --from=build /app/publish .

# Expose port 80
EXPOSE 80

# Set the entrypoint
ENTRYPOINT ["dotnet", "Metrics.Idle.dll"]