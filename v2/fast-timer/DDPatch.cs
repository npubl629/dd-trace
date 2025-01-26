using HarmonyLib;
using System.Reflection;

#pragma warning disable CS8601
#pragma warning disable CS8602
#pragma warning disable CS8618

public static class DDPatch
{
    private static bool _isInitialized = false;

    private static ConstructorInfo _publicConstructor;
    private static ConstructorInfo _internalConstructor;
    private static object _initializeListenerFunc;

    private static TimeSpan? _overrideDelay;

    public static void RunPatch(TimeSpan delay)
    {
        if (_isInitialized) return;

        _overrideDelay = delay;

        Assembly assembly = Assembly.GetAssembly(typeof(Datadog.Trace.Tracer))!;
        var RuntimeMetricsWriter = assembly.GetType("Datadog.Trace.RuntimeMetrics.RuntimeMetricsWriter");

        var constructors = RuntimeMetricsWriter.GetDeclaredConstructors();
        _publicConstructor = constructors.Single(x =>
            x.ToString() == "Void .ctor(Datadog.Trace.Vendors.StatsdClient.IDogStatsd, System.TimeSpan, Boolean)");

        _internalConstructor = constructors.Single(x =>
            x.ToString() == "Void .ctor(Datadog.Trace.Vendors.StatsdClient.IDogStatsd, System.TimeSpan, Boolean, System.Func`4[Datadog.Trace.Vendors.StatsdClient.IDogStatsd,System.TimeSpan,System.Boolean,Datadog.Trace.RuntimeMetrics.IRuntimeMetricsListener])");

        _initializeListenerFunc = RuntimeMetricsWriter.GetField("InitializeListenerFunc", BindingFlags.Static | BindingFlags.NonPublic).GetValue(null);

        bool b = true;
        var replacement = typeof(DDPatch).GetMethod(nameof(ReplacementConstructor), BindingFlags.Static | BindingFlags.NonPublic);

        var harmony = new Harmony("Datadog.Trace");

        harmony.Patch(_publicConstructor, prefix: new HarmonyMethod(replacement));

        _isInitialized = true;
    }

    private static bool ReplacementConstructor(ref object __instance, object statsd, TimeSpan delay, bool inAzureAppServiceContext)
    {
        _internalConstructor.Invoke(__instance, new object[] { statsd, _overrideDelay ?? delay, inAzureAppServiceContext, _initializeListenerFunc });
        return false;
    }
}

#pragma warning restore CS8601
#pragma warning restore CS8602
#pragma warning restore CS8618
