clean:
	@find . -name "__pycache__" -exec rm -rf {} \; || true
	@rm -f mensagens*.md

format:
	@find . -name "*.py" -exec black -v {} \; || true
	isort .