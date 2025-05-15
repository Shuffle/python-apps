import boto3
import json
import asyncio

from walkoff_app_sdk.app_base import AppBase

class AWSSQSApp(AppBase):
    __version__ = "1.0.0"
    app_name = "aws_sqs_app"
    
    def __init__(self, redis, logger, console_logger=None):
        super().__init__(redis, logger, console_logger)
    
    async def list_sqs_queues(self, region="us-east-1"):
        """
        Lista todas as filas SQS disponíveis na região especificada.
        Usa automaticamente as credenciais do IAM role.
        """
        try:
            # Criar sessão boto3 sem credenciais explícitas
            # Isso fará o boto3 usar o IAM role automaticamente
            session = boto3.Session(region_name=region)
            sqs = session.client('sqs')
            
            # Listar filas
            response = sqs.list_queues()
            
            queue_urls = response.get('QueueUrls', [])
            
            return json.dumps({
                "success": True,
                "queues": queue_urls,
                "count": len(queue_urls)
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao listar filas SQS: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    async def send_sqs_message(self, queue_url, message_body, region="us-east-1"):
        try:
            session = boto3.Session(region_name=region)
            sqs = session.client('sqs')
            
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )
            
            return json.dumps({
                "success": True,
                "message_id": response.get('MessageId')
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem SQS: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    async def receive_sqs_messages(self, queue_url, region="us-east-1", max_messages=1):
        """
        Recebe mensagens de uma fila SQS.
        """
        try:
            session = boto3.Session(region_name=region)
            sqs = session.client('sqs')
            
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=min(max_messages, 10),
                WaitTimeSeconds=0
            )
            
            messages = response.get('Messages', [])
            
            return json.dumps({
                "success": True,
                "message_count": len(messages),
                "messages": messages
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao receber mensagens SQS: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

if __name__ == "__main__":
    asyncio.run(AWSSQSApp.run(), debug=True)