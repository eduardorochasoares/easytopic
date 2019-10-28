#!/bin/bash
/opt/start.sh -y /opt/test/models/sample_english_nnet2.yaml
sleep 120
python worker.py