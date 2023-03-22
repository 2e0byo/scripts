.PHONY: install

install:
	find . -maxdepth 1 -type f -executable -exec ln -rs {} ~/.local/bin \;
