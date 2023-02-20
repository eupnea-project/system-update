#!/bin/bash

# Start in sub-thread to avoid package manager waiting for this script to finish
systemctl start eupnea-update.service &
