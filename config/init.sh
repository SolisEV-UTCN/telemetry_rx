#!/bin/bash
set -eo pipefail

# Clear previous dashboards
influx stacks | awk 'NR>1 {print $1}' | xargs -I{} influx stacks rm --stack-id {} --force yes
    
# Autoload templates
influx apply -o solis -f /etc/influx/templates --force yes
