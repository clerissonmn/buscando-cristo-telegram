clean:
	@find . -name "__pycache__" -exec rm -rf {} \; || true

format:
	@find . -name "*.py" -exec black -v {} \; || true
	isort .