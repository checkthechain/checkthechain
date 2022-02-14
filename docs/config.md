
# Configuration

`ctc` uses a configuration file to customize behavior and store frequently-used metadata like archive node info.

Running `ctc setup` in the terminal will start an interactive setup wizard that saves all configuration settings to a config file.

The most important configuration settings are:
- url's to archive node RPC providers
- the default network and provider to use
- where to store downloaded `ctc` data

The schema of the config file can be found in `ctc.spec.typedefs.config_types`. Config files that do not conform to this schema will not load.

