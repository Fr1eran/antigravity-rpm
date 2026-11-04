# ============================================================================
# .copr/Makefile — Universal COPR SRPM build integration
# ============================================================================

TOPDIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
spec ?= antigravity-ide.spec
SPEC ?= $(spec)
outdir ?= $(CURDIR)

# Resolve SPEC path (supports both relative and absolute paths passed by COPR)
SPEC_PATH := $(if $(filter /%,$(SPEC)),$(SPEC),$(TOPDIR)/$(SPEC))

URL_X64 := $(shell grep '^# URL_X64:' $(SPEC_PATH) | awk '{print $$3}')
URL_ARM64 := $(shell grep '^# URL_ARM64:' $(SPEC_PATH) | awk '{print $$3}')
SRC_X64 := $(shell grep '^Source0:' $(SPEC_PATH) | awk '{print $$2}')
SRC_ARM64 := $(shell grep '^Source1:' $(SPEC_PATH) | awk '{print $$2}')

.PHONY: srpm

srpm:
	@echo "Building SRPM for $(SPEC_PATH)..."
	@echo "Downloading x86_64 tarball ($(SRC_X64))..."
	curl -sSLf --retry 3 --connect-timeout 30 -o "$(TOPDIR)/$(SRC_X64)" "$(URL_X64)"
	@echo "Downloading aarch64 tarball ($(SRC_ARM64))..."
	curl -sSLf --retry 3 --connect-timeout 30 -o "$(TOPDIR)/$(SRC_ARM64)" "$(URL_ARM64)"
	@echo "Building SRPM in $(outdir)..."
	rpmbuild -bs \
		--define "_sourcedir $(TOPDIR)" \
		--define "_specdir $(TOPDIR)" \
		--define "_srcrpmdir $(outdir)" \
		"$(SPEC_PATH)"
	@echo "SRPM built successfully in $(outdir)"
