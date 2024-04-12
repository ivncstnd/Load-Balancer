#!/bin/bash

sudo ip link add link enp0s3 address 00:11:11:11:11:11 virtual0 type macvlan

sudo ifconfig virtual0 up

sudo ifconfig enp0s3 promisc