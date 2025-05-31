run_all:
	docker rm -f myrunningparser || true
	docker build -t myparser .
	docker run -d --name myrunningparser myparser
	sleep 2
	docker exec -it myrunningparser bash -c "cd /app/tests && pytest"
