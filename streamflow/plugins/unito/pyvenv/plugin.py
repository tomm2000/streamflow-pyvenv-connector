from streamflow.ext.plugin import StreamFlowPlugin

from .connector import PyVenvConnector

class PyVenvStreamFlowPlugin(StreamFlowPlugin):
    def register(self) -> None:
        self.register_connector("pyvenv", PyVenvConnector)