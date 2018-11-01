# GloboMap Core Loader

Application responsible for reading connected applications events and apply them to the [Globo Map API](https://github.com/globocom/globomap-api).
This application makes use of decoupled drivers for reading and transforming sources' information and make
them available for updating the [Globo Map API](https://github.com/globocom/globomap-api).

## Starting Project:

` make dynamic_ports` <br>
` make containers_build ` (Build images.) <br>
` make containers_start ` (Up containers) <br>

## Running local with docker:

` make dynamic_ports` <br>
` make containers_build ` (When project not started yet.) <br>
` make containers_start ` (When project not started yet.) <br>

## Running Tests:

` make containers_build ` (When project not started yet.) <br>
` make containers_start ` (When project not started yet.) <br>
` make tests `

## Deploy in Tsuru:

### Loader

` make deploy_loader project=<name of project> `<br>

## Environment variables configuration
All of the environment variables below must be set for the application to work properly.

### Loader
| Variable                           | Description                                                                | Example                             |
|------------------------------------|----------------------------------------------------------------------------|----------------------------------   |
| DRIVER_FETCH_INTERVAL              | Interval in seconds on which the updates are fetched from a driver         | 60 (default)                        |
| GLOBOMAP_API_URL                   | GloboMap API address                                                       | http://globomap.domain.com          |
| GLOBOMAP_API_USERNAME              | GloboMap API username                                                      | username                            |
| GLOBOMAP_API_PASSWORD              | GloboMap API password                                                      | xyz                                 |
| GLOBOMAP_RMQ_HOST                  | RabbitMQ host                                                              | rabbitmq.yourdomain.com             |
| GLOBOMAP_RMQ_PORT                  | RabbitMQ port                                                              | 5672 (default)                      |
| GLOBOMAP_RMQ_USER                  | RabbitMQ user                                                              | user-name                           |
| GLOBOMAP_RMQ_PASSWORD              | RabbitMQ password                                                          | password                            |
| GLOBOMAP_RMQ_VIRTUAL_HOST          | RabbitMQ virtual host                                                      | /globomap                           |
| GLOBOMAP_RMQ_QUEUE_NAME            | RabbitMQ queue name                                                        | globomap-updates                    |
| GLOBOMAP_RMQ_EXCHANGE              | RabbitMQ updates exchange name                                             | globomap-updates-exchange           |
| GLOBOMAP_RMQ_ERROR_EXCHANGE        | RabbitMQ error exchange name                                               | globomap-errors-exchange            |
| GLOBOMAP_RMQ_BINDING_KEY           | RabbitMQ generic driver API binding key                                    | globomap.updates (default)          |
| RETRIES                            | Number of retries.                                                         | 3                                   |
| FACTOR                             | Number of threads.                                                         | 1                                   |
| QUERIES                            | Queries                                                                    | query_name_test                     |
| ZBX_PASSIVE_MONITOR_LOADER         | Zabbix monitor                                                             | passive_abc_monitor_loader          |
| ZBX_PASSIVE_MONITOR_SCHED_QUERIES  | Zabbix monitor                                                             | passive_abc_monitor_sched_queries   |
| SENTRY_DSN                         | Destination Sentry server.                                                 | https://user:password@sentry.io/test|


### Environment variables configuration from external libs
All of the environment variables below must be set for the application to work properly.

[globomap-auth-manager](https://github.com/globocom/globomap-auth-manager)

## Licensing

GloboMap Core Loader is under [Apache 2 License](./LICENSE)
