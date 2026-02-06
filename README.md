# SLURM REST API Plugin for StreamFlow

## Installation 
<!-- **NOTE: not published on PyPI yet.**

Simply install the package directory from [PyPI]() using [pip](https://pip.pypa.io/en/stable/). StreamFlow will automatically recognise it as a plugin and load it at each workflow execution.
```bash
pip install streamflow-slurmrest
``` -->

Clone this repository and install the package directory using [pip](https://pip.pypa.io/en/stable/). StreamFlow will automatically recognise it as a plugin and load it at each workflow execution.
```bash
git clone https://github.com/tomm2000/streamflow-pyvenv-connector
cd streamflow-pyvenv-connector
pip install -e .
```


If everything worked correctly, whenever a workflow execution start the following message should be printed in the log:
```bash
Successfully registered plugin streamflow.plugins.unito.pyvenv.connector.PyVenvStreamFlowPlugin
```

## Usage
```yml
deployments:
  pyvenv-deployment:
    type: pyvenv
    config:
      path: /mnt/shared/tfogliobonda/tmp # path where the virtual environment will be created, optional, default is /tmp/streamflow-venv
      random-suffix: false # whether to add a random suffix to the virtual environment name, optional, default is true
      force-install: true # whether to force dependecy installation even if the virtual environment already exists, optional, default is false
      keep-venv: true # whether to keep the virtual environment after the workflow execution, optional, default is false
      requirements: # list of pip requirements to install in the virtual environment, optional, default is []
        - cowsay

          ...
```