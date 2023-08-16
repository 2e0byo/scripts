.PHONY: install

install:
	mkdir ~/.local/bin 2>/dev/null || true
	find . -maxdepth 1 -type f -executable -exec bash -c 'ln -rs {} ~/.local/bin 2>/dev/null || echo "Already installed: {}"' \;
