import json
import grpc
import ipaddress
import time
import yaml
from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc
from walkoff_app_sdk.app_base import AppBase


class Velociraptor(AppBase):

    __version__ = "1.0.0"
    app_name = "velociraptor"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def auth(self, api_config):
        credfile = self.get_file(api_config)["data"]
        config = yaml.load(credfile, Loader=yaml.FullLoader)
        creds = grpc.ssl_channel_credentials(
            root_certificates=config["ca_certificate"].encode("utf8"),
            private_key=config["client_private_key"].encode("utf8"),
            certificate_chain=config["client_cert"].encode("utf8")
        )

        return creds, config

    def request(self, api_config, query):
        creds = self.auth(api_config)[0]
        config = self.auth(api_config)[1]
        options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)
        with grpc.secure_channel(config["api_connection_string"], creds, options) as channel:
            stub = api_pb2_grpc.APIStub(channel)
            client_query = query
            client_request = api_pb2.VQLCollectorArgs(
                max_wait=60,
                Query=[api_pb2.VQLRequest(
                Name="ShuffleQuery",
                VQL=client_query,
            )])

            r = []
            for response in stub.Query(client_request):
                if response.Response:
                    r = r + json.loads(response.Response)
            return r

    def add_client_label(self, api_config, client_id, label):
        query = "SELECT label(client_id='" + client_id + "', labels=['" + label  +"'], op='set') FROM scope()'"
        results = self.request(api_config, query)
        return results


    def get_client_label(self, api_config, client_id, label):
        query = "SELECT label(client_id='" + client_id + "', labels=['" + label  +"'], op='check') FROM scope()'"
        results = self.request(api_config, query)
        return results

    def remove_client_label(self, api_config, client_id, label):
        query = "SELECT label(client_id='" + client_id + "', labels=['" + label  +"'], op='remove') FROM scope()'"
        results = self.request(api_config, query)
        return results


    def add_client_quarantine(self, api_config, client_id):
        query = 'SELECT collect_client(client_id="' + client_id + '", artifacts=["Windows.Remediation.Quarantine"], spec=dict(`Windows.Remediation.Quarantine`=dict())) FROM scope()' 
        results = self.request(api_config, query)
        return results

    def remove_client_quarantine(self, api_config, client_id):
        query = 'SELECT collect_client(client_id="' + client_id + '", artifacts=["Windows.Remediation.Quarantine"], spec=dict(`Windows.Remediation.Quarantine`=dict(`RemovePolicy`="Y"))) FROM scope()'
        results = self.request(api_config, query)
        return results

    def get_artifact_definitions(self, api_config):
        query = 'SELECT name, description, parameters FROM artifact_definitions(deps=True)'
        results = self.request(api_config, query)
        return results

    def get_client_id(self, api_config, host):
        try:
            if ipaddress.ip_address(host):
                query = "SELECT client_id FROM clients() WHERE last_ip =~ '" + host + "'"  
        except:
            query = "SELECT client_id FROM clients(search=" + host + ")"
        results = self.request(api_config, query)
        
        try:
            return {
                "success": True,
                "reason": results [0]['client_id']
            }
        except Exception as e: 
            return {
                "success": False,
                "reason": "An error happened getting client ID. This usually means the Client ID doesn't exist.",
                "details": f"{e}"
            }

    def get_client_flows(self, api_config, client_id):
        query = "SELECT * FROM flows(client_id='" + client_id  + "')"
        results = self.request(api_config, query)
        return results

    def get_client_flow_results(self, api_config, client_id, flow_id):
        state = self.get_client_flow_status(api_config, client_id, flow_id)
        while (state == "RUNNING"):
            state = self.get_client_flow_status(api_config, client_id, flow_id)
            if state == "FINISHED":
                break
            else:
                time.sleep(5)
        query = "SELECT * FROM flow_results(flow_id='" + flow_id  + "', client_id='" + client_id  + "')"
        results = self.request(api_config, query)
        return results[0]

    def get_client_flow_status(self, api_config, client_id, flow_id):
        query = "SELECT * FROM flows(flow_id='" + flow_id  + "', client_id='" + client_id  + "')"
        results = self.request(api_config, query)
        return results[0]['state']

    def get_hunt_flows(self, api_config, hunt_id):
        query = 'SELECT * FROM hunt_flows(hunt_id="' + hunt_id  + '")'
        results = results = self.request(api_config, query)
        return results[0]

    def get_hunt_results(self, api_config, hunt_id):
        query = 'SELECT * FROM hunt_results(hunt_id="' + hunt_id  + '")'
        results = results = self.request(api_config, query)
        return results

    def search_with_custom_query(self, api_config, query):
        results = results = self.request(api_config, query)
        return results

    def search_filename(self, api_config, filepath, filename):
        query = 'SELECT hunt(description=\"Shuffle Filename Hunt::' + filename + '\", expires=(now() + 60) * 1000000,artifacts=[\"Linux.Search.FileFinder\",\"MacOS.Search.FileFinder\","Windows.Forensics.FilenameSearch\"],spec=dict(`Linux.Search.FileFinder`=dict(`SearchFilesGlob`=\"' + filename + '\"),`MacOS.Search.FileFinder`=dict(`SearchFilesGlob`=\"' + filename + '\"),`Windows.Forensics.FilenameSearch`=dict(`yaraRule`=\"wide nocase:' + filepath + filename + '\"))) AS Hunt FROM scope()'
        results = self.request(api_config, query)
        return results[0]

    def search_hash(self, api_config, filehash):
        query = 'SELECT hunt(description=\"Shuffle Hash Hunt::' + filehash + '", expires=(now() + 60) * 1000000, artifacts=[\"Generic.Forensic.LocalHashes.Query\"],spec=dict(`Generic.Forensic.LocalHashes.Query`=dict(Hashes="Hash\\n' + filehash + '\\n"))) AS Hunt from scope()'
        results = results = self.request(api_config, query)
        return results[0]

if __name__ == "__main__":
    Velociraptor.run()
