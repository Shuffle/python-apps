from walkoff_app_sdk.app_base import AppBase
import asyncio

from thehive4py.api import TheHiveApi

class thehive4pyWrapper(AppBase):

    __version__ = "0.0.1"
    app_name = "thehive4py"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """

        super().__init__(redis, logger, console_logger)   
        self.wrapper = TheHiveApi(url="http://localhost:9000", principal="asd")

    async def do_patch(self, api_url, **attributes):
        return self.wrapper.do_patch(self, api_url, **attributes)
        
    async def health(self):
        return self.wrapper.health(self)
        
    async def get_current_user(self):
        return self.wrapper.get_current_user(self)
        
    async def create_case(case):
        return self.wrapper.create_case(case)
        
    async def update_case(case, fields=[]):
        return self.wrapper.update_case(case, fields=[])
        
    async def create_case_task(case_id, case_task):
        return self.wrapper.create_case_task(case_id, case_task)
        
    async def update_case_task():
        return self.wrapper.update_case_task()
        
    async def create_task_log(task_id, case_task_log):
        return self.wrapper.create_task_log(task_id, case_task_log)
        
    async def create_case_observable(case_id, case_observable):
        return self.wrapper.create_case_observable(case_id, case_observable)
        
    async def get_case(case_id):
        return self.wrapper.get_case(case_id)
        
    async def find_cases(self, **attributes):
        return self.wrapper.find_cases(self, **attributes)
        
    async def delete_case(case_id):
        return self.wrapper.delete_case(case_id)
        
    async def find_first(self, **attributes):
        return self.wrapper.find_first(self, **attributes)
        
    async def get_case_observables(case_id):
        return self.wrapper.get_case_observables(case_id)
        
    async def get_case_tasks(self, case_id, **attributes):
        return self.wrapper.get_case_tasks(self, case_id, **attributes)
        
    async def get_linked_cases(case_id):
        return self.wrapper.get_linked_cases(case_id)
        
    async def find_case_templates(self, **attributes):
        return self.wrapper.find_case_templates(self, **attributes)
        
    async def get_case_template(name):
        return self.wrapper.get_case_template(name)
        
    async def get_case_task(self, taskId):
        return self.wrapper.get_case_task(self, taskId)
        
    async def get_task_log(self, logId):
        return self.wrapper.get_task_log(self, logId)
        
    async def get_task_logs(taskId):
        return self.wrapper.get_task_logs(taskId)
        
    async def create_alert(alert):
        return self.wrapper.create_alert(alert)
        
    async def mark_alert_as_read(alert_id):
        return self.wrapper.mark_alert_as_read(alert_id)
        
    async def mark_alert_as_unread(alert_id):
        return self.wrapper.mark_alert_as_unread(alert_id)
        
    async def update_alert(alert_id):
        return self.wrapper.update_alert(alert_id)
        
    async def get_alert(alert_id):
        return self.wrapper.get_alert(alert_id)
        
    async def find_alerts(self, **attributes):
        return self.wrapper.find_alerts(self, **attributes)
        
    async def update_case_observables(observable):
        return self.wrapper.update_case_observables(observable)
        
    async def promote_alert_to_case(alert_id):
        return self.wrapper.promote_alert_to_case(alert_id)
        
    async def run_analyzer(cortex_id, artifact_id, analyzer_id):
        return self.wrapper.run_analyzer(cortex_id, artifact_id, analyzer_id)
        
    async def find_tasks(self, **attributes):
        return self.wrapper.find_tasks(self, **attributes)
        

if __name__ == "__main__":
    asyncio.run(thehive4pyWrapper.run(), debug=True)
