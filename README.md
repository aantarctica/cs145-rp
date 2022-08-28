# Level 4 implementation of the Pull-Centric UDP-based Protocol

## CS 145 Replacement Project

#### 2nd Semester, AY 2021-2022

### Overview

This program uses UDP to pull data from the server. Instead of receiving the payload all at once, it sends a series of pull packets to receive the payload in parts through data packets. Each successful pull from the server receives a data packet as a response containing the requested data, together with a challenge question. This challenge question is solved through Pollard's Rho Algorithm.

As the server can only process pull packets up to a limited size, this program includes a mechanism to adjust pull size accordingly. Upon reaching the last data packet, the program submits the whole payload it received for the checking done by the server.

The program runs on a Linux machine within the same VPC as the server through Amazon Web Services (AWS) Accounts provided for by the course handlers for the transactions to take place. The program is written in Python3. Environment settings are also provided as a guide for the program to run in the system that the user is using.

Trace files were generated with **tshark** and trace analysis was done using **Wireshark** on a Windows 10 System. Screenshots are provided at the end of this document with analysis for each trace file. These files are provided with the project code for the course handlers.

### Running the program

This program runs on a system with Python of version **at least 3.8.10**. The machine should also be at the s**ame network (AWS Virtual Private Cloud)** as the TGRS.

`python3 client.py -a <address> -s <server_port> -c <client_port> -i <unique_id>`

(optional: run multiple sequential transactions)

`python3 client.py -a <address> -s <server_port> -c <client_port> -i <unique_id> -d <number_of_transactions>`
