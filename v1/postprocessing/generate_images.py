import os
import requests
import datetime
import matplotlib.pyplot as plt

def get_data():
    start_time = datetime.datetime(2024, 7, 17, 18)
    end_time = start_time + datetime.timedelta(days=7)
    now = datetime.datetime(2025, 1, 21, 18)

    headers = {
        'DD-API-KEY': os.environ['DD-API-KEY'],
        'DD-APPLICATION-KEY': os.environ['DD-APPLICATION-KEY']
    }

    cpu_pointlists_by_container = {}
    mem_pointlists_by_service = {}

    while start_time <= now:
        cpu_batch_params = {
            'from': start_time.timestamp(),
            'to': end_time.timestamp(),
            'query': 'avg:container.cpu.usage{container_name:trace-metrics-healthcheck-1 OR container_name:trace-nometrics-healthcheck-1 OR container_name:trace-control-healthcheck-1} by {container_name}'
        }

        print(f'Querying batch, {cpu_batch_params}')

        cpu_json_batch = requests.get('https://api.datadoghq.com/api/v1/query', params=cpu_batch_params, headers=headers).json()
        cpu_series = cpu_json_batch['series']
        for i in range(len(cpu_series)):
            name = cpu_series[i]['tag_set'][0][len('container_name:'):]
            pointlist = cpu_series[i]['pointlist']
            if not name in cpu_pointlists_by_container:
                cpu_pointlists_by_container[name] = []
            cpu_pointlists_by_container[name] += pointlist

        mem_batch_params = {
            'from': start_time.timestamp(),
            'to': end_time.timestamp(),
            'query': 'ewma_5(avg:runtime.dotnet.mem.committed{service:metrics-healthcheck OR service:metrics-idle} by {service})'
        }

        mem_json_batch = requests.get('https://api.datadoghq.com/api/v1/query', params=mem_batch_params, headers=headers).json()
        mem_series = mem_json_batch['series']
        for i in range(len(mem_series)):
            name = mem_series[i]['tag_set'][0][len('service:'):]
            pointlist = mem_series[i]['pointlist']
            if not name in mem_pointlists_by_service:
                mem_pointlists_by_service[name] = []
            mem_pointlists_by_service[name] += pointlist

        start_time = end_time
        end_time = end_time + datetime.timedelta(days=7)

    cpu_data_by_container = {}
    for container_name in cpu_pointlists_by_container:
        values = cpu_pointlists_by_container[container_name]
        cpu_values = [item[1] / 1_000_000 for item in values] # convert microcores to millicores
        timestamps = [item[0] / 1000 for item in values] # convert ms since epoch to seconds since epoch
        dates = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
        cpu_data_by_container[container_name] = {'dates': dates, 'cpu_values': cpu_values}

    mem_data_by_service = {}
    for service in mem_pointlists_by_service:
        values = mem_pointlists_by_service[service]
        mem_values = [item[1] / (1024*1024) for item in values] # convert to MiB
        timestamps = [item[0] / 1000 for item in values] # convert ms since epoch to seconds since epoch
        dates = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
        mem_data_by_service[service] = {'dates': dates, 'mem_values': mem_values}

    return cpu_data_by_container, mem_data_by_service


def generate_cpu_chart(data_by_container):
    fig = plt.figure(figsize=(15, 5))
    fig.tight_layout(pad=3)
    ax = fig.add_subplot()
    ax.set_xlabel('Date')
    ax.set_ylabel('CPU Value (millicores)')
    ax.grid(True)
    ax.set_title(f'CPU Usage by Container')

    control = data_by_container['trace-control-healthcheck-1']['cpu_values']
    metrics = data_by_container['trace-metrics-healthcheck-1']['cpu_values']
    nometrics = data_by_container['trace-nometrics-healthcheck-1']['cpu_values']
    dates = data_by_container['trace-nometrics-healthcheck-1']['dates']

    ax.plot(dates, metrics, label='trace-metrics-healthcheck-1')
    ax.plot(dates, nometrics, label='trace-nometrics-healthcheck-1')
    ax.plot(dates, control, label='trace-control-healthcheck-1')
    ax.legend()

    return fig


def generate_cpu_diff_chart(data_by_container):
    fig = plt.figure(figsize=(15, 5))
    fig.tight_layout(pad=10)
    ax = fig.add_subplot()
    ax.set_xlabel('Date')
    ax.set_ylabel('CPU Difference (millicores)')
    ax.grid(True)
    ax.set_title(f'CPU Usage - Difference Between Services')
    control = data_by_container['trace-control-healthcheck-1']['cpu_values']
    metrics = data_by_container['trace-metrics-healthcheck-1']['cpu_values']
    nometrics = data_by_container['trace-nometrics-healthcheck-1']['cpu_values']
    dates = data_by_container['trace-nometrics-healthcheck-1']['dates']
    diff_metrics_control = [a - b for (a, b) in zip(metrics, control)]
    diff_metrics_nometrics = [a - b for (a, b) in zip(metrics, nometrics)]
    diff_nometrics_control = [a - b for (a, b) in zip(nometrics, control)]
    ax.plot(dates, diff_metrics_control, label='Healthcheck CPU Difference: Metrics - Control')
    ax.plot(dates, diff_nometrics_control, label='Healthcheck CPU Difference: NoMetrics - Control')
    ax.plot(dates, diff_metrics_nometrics, label='Healthcheck CPU Difference: Metrics - NoMetrics')
    ax.text(dates[-1], ax.get_xlim()[1] - 1, 'Test annotation')

    ax.legend()
    return fig

def generate_mem_chart(mem_data):
    fig = plt.figure(figsize=(15, 5))
    fig.tight_layout(pad=3)
    ax = fig.add_subplot()
    ax.set_xlabel('Date')
    ax.set_ylabel('.Net Committed Memory Value (MiB)')
    ax.grid(True)
    ax.set_title(f'.Net Committed Memory by Service')

    idle = mem_data['metrics-idle']['mem_values']
    healthcheck = mem_data['metrics-healthcheck']['mem_values']
    dates = mem_data['metrics-idle']['dates']

    ax.plot(dates, idle, label='metrics-idle')
    ax.plot(dates, healthcheck, label='metrics-healthcheck')
    ax.legend()

    return fig

if '__main__' == __name__:
    cpu_data, mem_data = get_data()

    fig1 = generate_cpu_chart(cpu_data)
    fig2 = generate_cpu_diff_chart(cpu_data)
    fig3 = generate_mem_chart(mem_data)

    fig1.savefig('cpu-usage.png')
    fig2.savefig('cpu-diff.png')
    fig3.savefig('mem-diff.png')
