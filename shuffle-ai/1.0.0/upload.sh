
gcloud run deploy shuffle-ai-1-0-0 \
	--region=europe-west2 \
	--max-instances=5 \
	--set-env-vars=SHUFFLE_APP_EXPOSED_PORT=8080,SHUFFLE_SWARM_CONFIG=run,SHUFFLE_LOGS_DISABLED=true,SHUFFLE_APP_SDK_TIMEOUT=120 --source=./  \
	--timeout=120s
