
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/status", () =>
{
    return "OK";
});
app.Run();
