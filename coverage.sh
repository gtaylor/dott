#!/bin/bash
PYTHONPATH=. nosetests -s --with-coverage --cover-html --cover-html-dir=cover_html --cover-package=src
