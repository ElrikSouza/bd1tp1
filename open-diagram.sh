#!/bin/bash

diagramHash=`cat docs/diagram-hash.txt`

firefox --new-tab "https://www.plantuml.com/plantuml/uml/${diagramHash}"