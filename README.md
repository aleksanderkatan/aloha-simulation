An implementation of continuous and slotted Aloha transfer protocols.  
The program simulates the protocol to measure empirically the amount of collisions and other statistics.

The implementation uses os.fork and therefore will not work on Windows system.

Example test:  
`./aloha.py --continuous --slot 0.01 --slots 1000 --clients 10 --packet-probability 0.01 --first-interval 0.1 --multiplier 2`

