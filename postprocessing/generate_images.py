import os
import requests
import datetime
import matplotlib.pyplot as plt

def get_data():
    start_time = datetime.datetime(2024, 7, 17, 18)
    end_time = start_time + datetime.timedelta(days=7)
    now = datetime.datetime.now()

    headers = {
        'DD-API-KEY': os.environ['DD-API-KEY'],
        'DD-APPLICATION-KEY': os.environ['DD-APPLICATION-KEY']
    }

    pointlists_by_container = {}

    while start_time <= now:
        batch_params = {
            'from': start_time.timestamp(),
            'to': end_time.timestamp(),
            'query': 'avg:container.cpu.usage{container_name:trace-metrics-healthcheck-1 OR container_name:trace-nometrics-healthcheck-1 OR container_name:trace-control-healthcheck-1} by {container_name}'
        }

        print(f'Querying batch, {batch_params}')

        json_batch = requests.get('https://api.datadoghq.com/api/v1/query', params=batch_params, headers=headers).json()

        series = json_batch['series']
        for i in range(len(series)):
            name = series[i]['tag_set'][0][len('container_name:'):]
            pointlist = series[i]['pointlist']
            if not name in pointlists_by_container:
                pointlists_by_container[name] = []
            pointlists_by_container[name] += pointlist

        start_time = end_time
        end_time = end_time + datetime.timedelta(days=7)

    data_by_container = {}
    for container_name in pointlists_by_container:
        values = pointlists_by_container[container_name]
        cpu_values = [item[1] / 1_000_000 for item in values] # convert microcores to millicores
        timestamps = [item[0] / 1000 for item in values] # convert ms since epoch to seconds since epoch
        dates = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
        data_by_container[container_name] = {'dates': dates, 'cpu_values': cpu_values}

    return data_by_container


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

if '__main__' == __name__:
    data_by_container = get_data()

    fig1 = generate_cpu_chart(data_by_container)
    fig2 = generate_cpu_diff_chart(data_by_container)

    fig1.savefig('cpu-usage.png')
    fig2.savefig('cpu-diff.png')
