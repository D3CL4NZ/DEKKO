#!/bin/bash

tmux new-session -s DEKKO 'bash --rcfile <(echo ". ~/.bashrc; ./bot.sh")';
