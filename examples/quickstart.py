import os
from runnee import Runnee

with Runnee(api_key=os.environ["RUNNEE_API_KEY"]) as client:
    result = client.execute(code="function main(){return 10+20;}", mode="dry-run")
    print(result)
