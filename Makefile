.PHONY: run run-docker test

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-docker:
	docker build -t job-tailor-agent .
	docker run -p 8000:8000 --env-file .env job-tailor-agent

test:
	pytest -q

