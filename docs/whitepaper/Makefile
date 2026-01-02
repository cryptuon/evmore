# EVMORE Whitepaper Makefile

# Main document name (without extension)
MAIN = evmore-whitepaper

# LaTeX compiler
LATEX = pdflatex

# Flags for pdflatex
LATEXFLAGS = -interaction=nonstopmode -halt-on-error

# Output directory
OUTDIR = build

# Default target
all: $(MAIN).pdf

# Create output directory
$(OUTDIR):
	mkdir -p $(OUTDIR)

# Build PDF (run twice for TOC and references)
$(MAIN).pdf: $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex

# Quick build (single pass, for drafts)
quick: $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex

# Clean auxiliary files
clean:
	rm -f $(MAIN).aux $(MAIN).log $(MAIN).out $(MAIN).toc
	rm -f $(MAIN).lof $(MAIN).lot $(MAIN).fls $(MAIN).fdb_latexmk
	rm -f $(MAIN).synctex.gz

# Clean everything including PDF
distclean: clean
	rm -f $(MAIN).pdf

# View the PDF (Linux)
view: $(MAIN).pdf
	xdg-open $(MAIN).pdf 2>/dev/null || open $(MAIN).pdf 2>/dev/null || evince $(MAIN).pdf

# Continuous build (requires latexmk)
watch:
	latexmk -pdf -pvc $(MAIN).tex

# Help
help:
	@echo "EVMORE Whitepaper Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build the PDF (default)"
	@echo "  quick     - Single-pass build for drafts"
	@echo "  clean     - Remove auxiliary files"
	@echo "  distclean - Remove all generated files"
	@echo "  view      - Open the PDF"
	@echo "  watch     - Continuous build with latexmk"
	@echo "  help      - Show this help"

.PHONY: all quick clean distclean view watch help
