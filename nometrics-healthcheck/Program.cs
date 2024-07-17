
// Initialize Datadog Tracing
using Datadog.Trace.Configuration;
using Datadog.Trace;

var tracerSettings = TracerSettings.FromDefaultSources();
Tracer.Configure(tracerSettings);

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/status", () =>
{
    using (var scope = Tracer.Instance.StartActive("web.request"))
    {
        return "OK";
    }
});
app.Run();
