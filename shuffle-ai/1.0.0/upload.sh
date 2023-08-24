
gcloud run deploy shuffle-ai-1-0-0 \
	--region=europe-west2 \
	--max-instances=3 \
	--set-env-vars=SHUFFLE_APP_EXPOSED_PORT=8080,SHUFFLE_SWARM_CONFIG=run,SHUFFLE_LOGS_DISABLED=true --source=./  \
	--timeout=1800s
