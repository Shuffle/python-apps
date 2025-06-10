import json
import ast
import redis

from walkoff_app_sdk.app_base import AppBase

class REDIS(AppBase):
    __version__ = "1.0.0"
    app_name = "Redis"

    def __init__(self, redis, logger, console_logger=None):
        print("INIT")
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    def set_value(self, server, port, key, value, nx, ex = None, password = None, database = 0):
        """
        Sets a key-value pair in Redis.
        """

        if password == None:
            redis_client = redis.Redis(decode_responses=True, host=server, port=port, db=database)
        else:
            redis_client = redis.Redis(decode_responses=True, password=password, port=port, host=server, db=database)
            
        
        result = redis_client.set(name=key, value=value, nx=nx, ex=ex)  # nx=True ensures "set only if the key does not exist"
        print(result)
        if result:  # If result is True, the key was successfully set
            print(f"Success: Key {key} set with value '{value}'")
            return {"success": True}
        else:
            print(f"Failed: Key {key} already exists.")
            return {"success": False}
    
    def get_value(self, server, port, key, password = None, database = 0):
        """
        Gets a value for a key in Redis.
        """
        if password == None:
            redis_client = redis.Redis(decode_responses=True, host=server, port=port, db=database)
        else:
            redis_client = redis.Redis(decode_responses=True, password=password, port=port, host=server, db=database)   
    
        result = redis_client.get(name=key)
        if result:
            return {"success": True, "value": result}
        else:
            return {"success": False, "error": f"Key {key} does not exist", "value": None}
        
        
if __name__ == "__main__":
    REDIS.run()
